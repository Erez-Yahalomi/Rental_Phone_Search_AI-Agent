y
from fastapi import APIRouter, HTTPException
from typing import List
from apps.api.schemas import StartCallsRequest, StartCallsResponse
from apps.storage.repositories import ListingRepository, ConversationRepository
from apps.workflow.jobs import CallJob
from apps.workflow.scheduler import Scheduler
from apps.workflow.rate_limit import TokenBucket
from apps.conversation.prompts import build_question_set
from apps.telephony.voice_gateway import VoiceGateway
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class CallExecutor:
    """
    Executes call jobs: create conversation record, place call via Twilio,
    attach questions and initialize state so webhooks can pick up.
    """
    def __init__(self, voice: VoiceGateway):
        self.voice = voice
        self.convo_repo = ConversationRepository()
        self.listing_repo = ListingRepository()

    def execute(self, job: CallJob) -> None:
        if not job.to_number:
            logger.info("Skipping job %s: no phone number", job.listing_id)
            return

        # Create placeholder conversation before dialing
        convo = self.convo_repo.get_or_create(call_sid=None, listing_id=job.listing_id)

        # Place call and obtain real CallSid
        try:
            call_sid = self.voice.place_call(job.to_number, webhook_path="/twilio/voice")
            logger.info("Placed call for listing %s -> %s (CallSid=%s)", job.listing_id, job.to_number, call_sid)
        except Exception as e:
            logger.exception("Failed to place call for listing %s to %s: %s", job.listing_id, job.to_number, e)
            return

        # Update conversation to use real call SID and attach questions
        self.convo_repo.update(call_sid=call_sid, state="INTRO", answers={})
        self.convo_repo.attach_questions(call_sid=call_sid, questions=job.questions)
        logger.info("Attached %d questions to conversation %s", len(job.questions), call_sid)


@router.post("/start", response_model=StartCallsResponse)
def start_calls(req: StartCallsRequest):
    """
    Create call jobs from stored listings and start scheduler in background threads.
    Returns number scheduled immediately; jobs process asynchronously.
    """
    repo = ListingRepository()
    listings = repo.list_by_search_id(req.search_id)

    if not listings:
        raise HTTPException(status_code=404, detail="No listings found for search_id")

    questions = build_question_set(req.user_questions or [])
    jobs: List[CallJob] = []
    for l in listings[: settings.MAX_LISTINGS_PER_SEARCH]:
        jobs.append(CallJob(
            listing_id=l["listing_id"],
            to_number=l.get("contact_phone"),
            questions=questions,
            search_id=req.search_id
        ))

    voice = VoiceGateway()
    executor = CallExecutor(voice=voice)
    rate_limit = TokenBucket(rate_per_sec=1.0, burst=10)
    scheduler = Scheduler(executor=executor, concurrency=settings.CALL_CONCURRENCY, rate_limit=rate_limit)
    scheduler.submit(jobs)
    scheduler.start()

    logger.info("Scheduled %d calls for search_id=%s", len(jobs), req.search_id)
    return StartCallsResponse(scheduled=len(jobs))
