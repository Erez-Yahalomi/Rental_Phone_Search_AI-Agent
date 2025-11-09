<h1>Rental AI Agent - Automated Rental Finder & Voice conversation call, Transcription Pipeline</h1> <p class="lead">Finding an apartment or house to rent is a long and tiresome process that involves searching real estate rental websites, then making numerous phone calls and having conversations with apartment and house owners or agents. To solve this problem, This repository is first to suggest  an  AI agent that quickly identify the best rental properties, collect relevant information efficiently, and get concise summaries without manually calling dozens of landlords. This AI agent can be applied to website listings for: real estate, cars, markets etc’. For finding listings according to the user preferences, then the AI agent calls the phone numbers in the listings, asks questions about the property or product, including questions prepared by the user, summarizes the phone conversations, and presents the summarized information in a dashboard.</p> </div> </header>

<div class="grid"> <main> <section class="card" aria-labelledby="overview-title"> <h2 id="overview-title" class="section-title">Overview</h2> <p class="muted"> This system is an AI agent system for  finding a residency for rent. It integrates with RentPath’s API to fetch rental listings based on user filters (city, price, beds, baths). Places automated  voice calls to the contact numbers in those listings, via Twilio, powered by GPT dialogue engine that handles clarifications and follow-ups,. Conducts dynamic conversations with land lords or property managers, asks default + user‑defined questions. Handles implicit or ambiguous answers with clarifications. Stores summaries of each call + rental details in a dashboard for easy review. This systemt is built with Python (FastAPI), Twilio for voice, a relational database for persistence, and an LLM for natural language tasks. </p> </section>

<section class="card" aria-labelledby="features-title" style="margin-top:16px;"> <h2 id="features-title" class="section-title">Features</h2> <ul> <li>Ingest rental listings from RentPath (configurable)</li> <li>Place outbound voice calls and capture speech via Twilio</li> <li>GPT-powered DialogueManager for dynamic clarifications and question flow</li> <li>GPT-based summarization for human-readable conversation summaries</li><li>Handles up to 300 listings per search<li>SQL persistence for listings, conversations, and summaries</li> <li>Dashboard to browse summaries and listing details</li> </ul> </section>

<section class="card" aria-labelledby="quickstart-title" style="margin-top:16px;"> <h2 id="quickstart-title" class="section-title">Quickstart</h2> <p class="muted">Follow these steps to run locally:</p> <ol class="muted"> <li>Build the directory and copy the files according to, Project layout, file .</li> <li>Copy the example env file and fill credentials (database, Twilio, listing provider, OpenAI): <code>cp .env.example .env</code>.</li> <li>Create a virtual environment and install dependencies: <pre><code>python3 -m venv .venv && source .venv/bin/activate pip install -r requirements.txt</code></pre> </li> <li>Start the API server: <pre><code>bash run.sh</code></pre> </li> </ol> </section>

<section class="card" aria-labelledby="env-title" style="margin-top:16px;"> <h2 id="env-title" class="section-title">Environment variables</h2> <p class="muted">Important variables you should set in <code>.env</code>:</p> <ul> <li><code>DATABASE_URL</code> — Postgres connection string</li> <li><code>TWILIO_ACCOUNT_SID</code>, <code>TWILIO_AUTH_TOKEN</code>, <code>TWILIO_CALLER_ID</code></li> <li><code>RENTPATH_API_KEY</code> or your chosen listings provider key</li> <li><code>PUBLIC_BASE_URL</code> — publicly reachable URL for Twilio webhooks</li> <li><code>OPENAI_API_KEY</code> — required for GPT features</li> </ul> </section>

<section class="card" aria-labelledby="api-title" style="margin-top:16px;"> <h2 id="api-title" class="section-title">API Endpoints</h2> <div class="muted"> Use these endpoints during development and testing. <div style="margin-top:10px;"> <div class="meta">Ingest listings</div> <div class="endpoint">POST /listings/search</div> <pre class="muted"><code>{ "search_id": "latest", "city": "Austin", "state": "TX", "min_price": 1200, "max_price": 2500, "beds": 2, "baths": 1, "user_questions": ["Is there in-unit laundry?"] }</code></pre>

<div class="meta" style="margin-top:8px;">Start calls</div> <div class="endpoint">POST /calls/start</div> <pre class="muted"><code>{ "search_id": "latest", "user_questions": ["Do you offer short-term leases?"] }</code></pre>

 
<section class="card" aria-labelledby="examples-title" style="margin-top:16px;"> <h2 id="examples-title" class="section-title">Example call flow</h2> <ol class="muted"> <li>Scheduler creates a CallJob for a listing and places a call via Twilio.</li> <li>Twilio invokes the webhook, which runs the DialogueManager and returns TwiML prompts.</li> <li>Speech is transcribed (Twilio) and passed to the DialogueManager; GPT may generate clarifications.</li> <li>When the dialogue finishes, a human-friendly summary is generated and stored.</li> <li>Summaries are visible in the dashboard for review and follow-up.</li> </ol> </section>

<section class="card" aria-labelledby="troubleshoot-title" style="margin-top:16px;"> <h2 id="troubleshoot-title" class="section-title">Troubleshooting & tips</h2> <ul class="muted"> <li>Verify your public webhook URL (ngrok or a cloud endpoint) so Twilio can reach the webhook.</li> <li>Test your OpenAI key with a small script before enabling live calls to confirm connectivity and permissions.</li> <li>Watch logs for GPT latency — consider short placeholder prompts if calls time out while awaiting GPT responses.</li> <li>Use one test phone number during development to avoid unintentional outreach volume.</li> </ul> </section> </main>

<aside> <div class="card"> <div style="display:flex; justify-content:space-between; align-items:center;"> <div>
 <section>
  <h2>📞 Demo: Example Phone Conversation (San Francisco Apartment)</h2>
  <div>
    <strong>Agent (Twilio AI voice):</strong>
    <ul>
      <li>"Hello, I am calling regarding your apartment listing."</li>
      <li>"Are there external noises that are heard inside the apartment?"</li>
    </ul>
  </div>
  <div>
    <strong>Renter (Speech → Transcribed):</strong>
    <ul>
      <li>"It’s a quiet neighborhood, you don’t hear much traffic."</li>
    </ul>
  </div>
  <div>
    <strong>Agent:</strong>
    <ul>
      <li>"What is the monthly rent?"</li>
    </ul>
  </div>
  <div>
    <strong>Renter:</strong>
    <ul>
      <li>"It is $3,200 per month."</li>
    </ul>
  </div>
  <div>
    <strong>Agent:</strong>
    <ul>
      <li>"Is the deposit refundable?"</li>
    </ul>
  </div>
  <div>
    <strong>Renter:</strong>
    <ul>
      <li>"Yes, it is fully refundable after inspection."</li>
    </ul>
  </div>
  <div>
    <strong>Agent:</strong>
    <ul>
      <li>"What is the minimum lease period?"</li>
    </ul>
  </div>
  <div>
    <strong>Renter:</strong>
    <ul>
      <li>"One year."</li>
    </ul>
  </div>
  <div>
    <strong>Agent:</strong>
    <ul>
      <li>"Are pets allowed?"</li>
    </ul>
  </div>
  <div>
    <strong>Renter:</strong>
    <ul>
      <li>"Yes, cats and small dogs are welcome."</li>
    </ul>
  </div>
  <div>
    <strong>Agent:</strong>
    <ul>
      <li>"Thank you for your time. Goodbye."</li>
    </ul>
  </div>
</section>
 <img width="512" height="700" alt="image" src="https://github.com/user-attachments/assets/8894ef06-c9ff-4bc3-a8cf-be038cad7b25" />

</p>
 
