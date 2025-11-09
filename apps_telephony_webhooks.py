
from fastapi import APIRouter, Request, Response
from apps.conversation.gpt_dialogue_manager import GPTDialogueManager, DialogueState
from apps.conversation.summarizer import summarize_conversation
from apps.storage.repositories import ConversationRepository, ListingRepository

router = APIRouter()

@router.post("/twilio/voice")
async def twilio_voice(request: Request):
    """
    Twilio webhook handler:
    - Receives SpeechResult from Twilio <Gather>.
    - Advances GPTDialogueManager state.
    - Returns TwiML with next prompt.
    """
    form = await request.form()
    call_sid = form.get("CallSid")
    speech_result = form.get("SpeechResult")
    listing_id = form.get("listing_id")  # optional, can be passed in initial TwiML

    convo_repo = ConversationRepository()
    listing_repo = ListingRepository()

    convo = convo_repo.get_or_create(call_sid=call_sid, listing_id=listing_id or "")
    listing = listing_repo.get_by_id(convo.listing_id) if convo.listing_id else None

    # Initialize GPTDialogueManager
    dm = GPTDialogueManager(
        listing_context={
            "address": getattr(listing, "address", None),
            "title": getattr(listing, "title", None),
        },
        questions=convo.questions or []
    )

    # Restore state/answers if conversation already exists
    if convo.state:
        try:
            dm.state = DialogueState[convo.state]
        except KeyError:
            pass
    if convo.answers:
        dm.answers = dict(convo.answers)

    # Apply incoming speech
    if speech_result:
        dm.handle_response(speech_result)

    # Generate next prompt (pass last response for clarifications)
    prompt = dm.next_prompt(last_response=speech_result)
    new_state = dm.state.name

    # Persist state and answers
    convo_repo.update(call_sid=call_sid, state=new_state, answers=dm.answers)

    # If conversation ended, save summary
    if new_state == "END" and listing:
        summary = summarize_conversation({"address": listing.address, "title": listing.title}, dm.answers)
        convo_repo.save_summary(call_sid=call_sid, summary=summary)

    # Return TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{prompt}</Say>
    <Gather input="speech" action="/twilio/voice" method="POST" timeout="5">
        <Say voice="alice">Please respond.</Say>
    </Gather>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
