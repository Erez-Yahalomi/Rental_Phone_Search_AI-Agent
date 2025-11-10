 
<h1>Rental AI Agent - Automated Rental Finder & Voice conversation call, Transcription Pipeline</h1> <p class="lead">Finding an apartment or house to rent is a long and tiresome process that involves searching real estate rental websites, then making numerous phone calls and having conversations with apartment and house owners or agents. To solve this problem, This repository is first to suggest  an  AI agent that quickly identify the best rental properties, collect relevant information efficiently, and get concise summaries without manually calling dozens of landlords. This AI agent can be applied to website listings for: real estate, cars, staff merketplace etc’. For finding listings according to the user preferences, then the AI agent calls the phone numbers in the listings, asks questions about the property or product, including questions prepared by the user, summarizes the phone conversations, and presents the summarized information in a dashboard.</p> </div> </header>

<div class="grid"> <main> <section class="card" aria-labelledby="overview-title"> <h2 id="overview-title" class="section-title">Overview</h2> <p class="muted"> This system is an AI agent system for  finding a residency for rent. It integrates with Zillow’s website API to fetch rental listings based on user filters (city, price, beds, baths). Places automated  voice calls to the contact numbers in those listings, via Twilio, powered by GPT dialogue engine that handles clarifications and follow-ups,. Conducts dynamic conversations with land lords or property managers, asks default + user‑defined questions. Handles implicit or ambiguous answers with clarifications. Stores summaries of each call + rental details in a dashboard for easy review. This systemt is built with Python (FastAPI), Twilio for voice, a relational database for persistence, and an LLM for natural language tasks. </p> </section>

<section class="card" aria-labelledby="features-title" style="margin-top:16px;"> <h2 id="features-title" class="section-title">Features</h2> <ul> <li>Ingest rental listings from  Zillow (configurable)</li> <li>Place outbound voice calls and capture speech via Twilio</li> <li>GPT-powered DialogueManager for dynamic clarifications and question flow</li> <li>GPT-based summarization for human-readable conversation summaries</li><li>Handles up to 300 listings per search<li>SQL persistence for listings, conversations, and summaries</li> <li>Dashboard to browse summaries and listing details</li> </ul> </section>
## Quickstart

<section class="card" aria-labelledby="quickstart-title" style="margin-top:16px;"> <h2 id="quickstart-title" class="section-title">Quickstart</h2> <p class="muted">Follow these steps to run locally:</p> <ol class="muted"> <li>Build the directory and copy the files according to, Project layout, file .</li> <li>Copy the example env file and and set `LISTING_PROVIDER=zillow`. Fill credentials (database, Twilio, listing provider, OpenAI): </code>.</li> <li>Create a virtual environment and install dependencies: <pre><code>python3 -m venv .venv && source .venv/bin/activate pip install -r requirements.txt</code></li> <li>Start the API server: <pre><code>bash run.sh</code></pre> </li> </ol> </section>

<section class="card" aria-labelledby="env-title" style="margin-top:16px;"> <h2 id="env-title" class="section-title">Environment variables</h2> <p class="muted">Important variables you should set in <code>.env</code>:</p> <ul> <li><code>DATABASE_URL</code> — Postgres connection string</li> <li><code>TWILIO_ACCOUNT_SID</code>, <code>TWILIO_AUTH_TOKEN</code>, <code>TWILIO_CALLER_ID</code></li><li><code>Zillow_API_KEY, Zillow (partner / licensed scraper)or ZILLOW_SCRAPER_API_KEY — token for your chosen scraper service<code><li>ZILLOW_BASE_URL — partner API base URL (e.g., `https://api.zillow.com`)</code><li>ZILLOW_SCRAPER_SERVICE — scraper service name if using a licensed scraper (e.g., `apify`, `zenrows`, `scraperapi`)</li><li><code>PUBLIC_BASE_URL</code> — publicly reachable URL for Twilio webhooks</li><li><code>OPENAI_API_KEY</code> — required for GPT features </p> </section>
 
<section class="card" aria-labelledby="api-title" style="margin-top:16px;"> <h2 id="api-title" class="section-title">API Endpoints</h2> <div class="muted"> Use these endpoints during development and testing. <div style="margin-top:10px;"> <div class="meta">Ingest listings</div> <div class="endpoint">POST /listings/search</div> <pre class="muted"><code>{ "search_id": "latest", "city": "Austin", "state": "TX", "min_price": 1200, "max_price": 2500, "beds": 2, "baths": 1, "user_questions": ["Is there in-unit laundry?"] }</code></pre>

<div class="meta" style="margin-top:8px;">Start calls</div> <div class="endpoint">POST /calls/start</div> <pre class="muted"><code>{ "search_id": "latest", "user_questions": ["Do you offer short-term leases?"] }</code></pre>

 
<section class="card" aria-labelledby="examples-title" style="margin-top:16px;"> <h2 id="examples-title" class="section-title">Example call flow</h2> <ol class="muted"> <li>Scheduler creates a CallJob for a listing and places a call via Twilio.</li> <li>Twilio invokes the webhook, which runs the DialogueManager and returns TwiML prompts.</li> <li>Speech is transcribed (Twilio) and passed to the DialogueManager; GPT may generate clarifications.</li> <li>When the dialogue finishes, a human-friendly summary is generated and stored.</li> <li>Summaries are visible in the dashboard for review and follow-up.</li> </ul> </section>

<section aria-labelledby="legal-compliance" style="font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; max-width:900px; margin:0 auto; padding:18px; background:#fff; border:1px solid #eef4fb; border-radius:10px;"> <h2 id="legal-compliance" style="margin:0 0 8px 0; font-size:18px; color:#0f1724;">Legal and compliance</h2> <p style="margin:0 0 12px 0; color:#556170; line-height:1.5;">Zillow does not provide a general public scraping API. Use only licensed Zillow partner APIs or authorized scraping services (for example, Apify, ZenRows, ScraperAPI) for ingesting Zillow listings.</li></ol> </section>
<aside><div class="card"> <div style="margin-top:16px;"> <div>
 <section>
  <h2>📞 Demo: Example Phone Conversation (San Francisco Apartment)</h2>
      <li><strong>Agent (Twilio AI voice):</strong>
      <li>"Hello, I am calling regarding your apartment listing."</li>
      <li>"Are there external noises that are heard inside the apartment?"</li>
      <li><strong>Renter (Speech → Transcribed):</strong>
      <li>"It’s a quiet neighborhood, you don’t hear much traffic."</li>
      <li><strong>Agent:</strong>
      <li>"What is the monthly rent?"</li>
      <li><strong>Renter:</strong>
      <li>"It is $3,200 per month."</li>
      <li><strong>Agent:</strong>
      <li>"Is the deposit refundable?"</li>
      <li><strong>Renter:</strong>
      <li>"Yes, it is fully refundable after inspection."</li>
      <li><strong>Agent:</strong>
       <li>"What is the minimum lease period?"</li>
       <li><strong>Renter:</strong>
       <li>"One year."</li>
       <li><strong>Agent:</strong>
       <li>"Thank you for your time. Goodbye."</li>
  

</section>
 <img width="512" height="700" alt="image" src="https://github.com/user-attachments/assets/8894ef06-c9ff-4bc3-a8cf-be038cad7b25" />

</p>
 
