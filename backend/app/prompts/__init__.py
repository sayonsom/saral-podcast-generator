"""LLM prompts for podcast script generation."""

# Character profiles
DOUG_PROFILE = {
    "name": "Doug Morrison",
    "role": "Host",
    "background": "35 years at FERC, retired Deputy General Counsel. Georgetown Law. Started when PURPA was new.",
    "political_lean": "Conservative, free-market, skeptical of subsidies",
    "speech_patterns": [
        "Long pauses before making a point",
        "References to specific docket numbers",
        "Rhetorical questions",
        "Self-deprecating humor about his age"
    ],
    "catchphrases": [
        "Well now, let me tell you...",
        "Back when Order 888 was just a gleam in someone's eye...",
        "The market has a way of sorting these things out",
        "I've seen this movie before"
    ],
    "expertise": ["FERC precedent", "Wholesale markets", "Transmission policy", "Rate cases"]
}

CLAIRE_PROFILE = {
    "name": "Claire Nakamura",
    "role": "Commentator",
    "background": "15 years energy consulting. McKinsey partner, now Lead at Espresso Consulting. Stanford MBA, Berkeley engineering.",
    "political_lean": "Progressive, pro-innovation, pragmatic about policy",
    "speech_patterns": [
        "Leads with data and charts (describes them)",
        "Client anecdotes (anonymized)",
        "Frameworks and mental models",
        "Acknowledges complexity"
    ],
    "catchphrases": [
        "The data actually shows...",
        "I was just talking to a utility exec who said...",
        "Let me offer a different framing here",
        "Doug, you're not wrong, but..."
    ],
    "expertise": ["Utility strategy", "DER economics", "Rate design", "Customer engagement"]
}


BLOG_ANALYSIS_PROMPT = """You are an energy industry analyst preparing a podcast brief.

Analyze this blog post and extract:
1. KEY_FACTS: Specific data points, statistics, dates, figures (be precise)
2. MAIN_ARGUMENTS: Core thesis and supporting claims
3. STAKEHOLDERS: Who is affected (utilities, consumers, regulators, startups, IPPs, etc.)
4. CONTROVERSY_POINTS: Elements that could spark debate between a conservative FERC lawyer and a progressive consultant
5. REGULATORY_HOOKS: Any FERC, PUC, state, or federal policy implications

Blog Content:
{blog_content}

Respond with valid JSON using exactly these keys: key_facts, main_arguments, stakeholders, controversy_points, regulatory_hooks.
Each value should be a list of strings."""


RESEARCH_EXPANSION_PROMPT = """You are a senior energy economist with 25+ years advising utilities, regulators, and investors.

Given these facts from Dr. Cheyenne's blog at askespresso.com:
{key_facts}

Generate deeper insights a senior professional would draw out:

SECOND_DEGREE_INSIGHTS (direct implications):
- What does this mean for utility integrated resource planning (IRP)?
- How might this affect pending or future rate cases?
- What startup opportunities or threats emerge?
- Which utilities are most exposed or advantaged?

THIRD_DEGREE_INSIGHTS (downstream effects):
- Long-term grid architecture implications (5-10 year horizon)
- Consumer behavior and adoption curve changes
- Market structure evolution and new business models
- Regulatory precedent risks or opportunities
- Cross-sector impacts (EVs, buildings, industry)

EXPERT_QUESTIONS (what sophisticated stakeholders would ask):
- What would a FERC commissioner want clarified?
- What would a utility CFO need for the board?
- What would a cleantech VC focus due diligence on?
- What would a state PUC staffer flag for commissioners?

Be specific. Reference actual market dynamics, real regulatory frameworks, and historical parallels.
Think like a partner at a top energy consulting firm briefing a CEO.

Respond with valid JSON using keys: utilities, consumers, startups, regulatory, expert_questions.
Each should be a list of 3-5 insightful strings."""


SCRIPT_OUTLINE_PROMPT = """Create a podcast script outline for "Energy Debates" episode.

CHARACTERS:
- DOUG (Host): {doug_profile}
- CLAIRE (Commentator): {claire_profile}

TOPIC: {topic}
KEY FACTS FROM BLOG: {key_facts}
EXPANDED INSIGHTS: {insights}
PREVIOUS EPISODE SUMMARY (for callbacks): {previous_summary}

Create a structured outline:

1. COLD_OPEN (2 min)
   - Light banter: weather, industry gossip, personal anecdote
   - Brief callback to previous episode if relevant
   - Natural transition to topic

2. TOPIC_INTRO (3 min)
   - Doug introduces with gentle skepticism
   - Sets up the debate framing
   - Mentions "Dr. Cheyenne's blog at askespresso.com"

3. MAIN_SEGMENTS (12-15 min total, 3-4 segments)
   For each segment:
   - Doug's position (regulatory/market perspective)
   - Claire's counter (data/innovation perspective)
   - [HUMOR_BEAT] marker for joke opportunity
   - Point of agreement (important - they're friends)

4. STAKEHOLDER_ROUNDUP (3 min)
   - Utilities: What should they do Monday morning?
   - Consumers: What does this mean for bills/choices?
   - Startups: Where's the opportunity?
   - Quick regulatory watch items

5. CLOSE (2 min)
   - Key takeaways (one from each host)
   - Teaser for next episode topic
   - Friendly sign-off with personality

Mark [HUMOR_BEAT] where natural humor should go.
Include at least 2 references to "Dr. Cheyenne's blog at askespresso.com".

Respond as structured text outline with clear section headers."""


FULL_SCRIPT_PROMPT = """Write the complete podcast script based on this outline.

OUTLINE:
{outline}

CHARACTER VOICE GUIDE:

DOUG (Host):
- Formal but warm, like a favorite law professor
- Historical references to FERC cases and orders
- Asks probing questions, not attacks
- Admits when markets surprise him
- Dry, understated humor
- Uses: "Well now...", "Back in my FERC days...", "The docket says..."
- Occasionally sighs at regulatory complexity

CLAIRE (Commentator):
- Consultant-speak but self-aware about it (sometimes jokes about McKinsey)
- Leads with data, not ideology
- Acknowledges implementation challenges
- Respects Doug's regulatory knowledge
- Sharp but kind wit
- Uses: "The numbers tell us...", "Our clients are seeing...", "Let me push back..."
- Occasionally gets excited about innovation

STYLE RULES:
- Natural speech: occasional "um", "well", "you know" (sparingly)
- Stage directions: [laughs], [sighs], [paper shuffling], [sips coffee]
- Timing markers every 5 min: [00:00], [05:00], [10:00]...
- Both hosts are LIKEABLE - disagreement with mutual respect
- Real humor from shared history and self-awareness
- Doug admits when Claire has a point (and vice versa)
- Inside jokes reward loyal listeners
- NO strawmanning - both positions have genuine merit
- They sometimes finish each other's thoughts

LENGTH TARGET: {duration_minutes} minutes of dialogue (roughly {word_count} words)
HUMOR LEVEL: {humor_level}/5 (1=serious, 5=comedy podcast)

ATTRIBUTION: Reference "Dr. Cheyenne's blog at askespresso.com" exactly twice.

Format output as:
[TIMESTAMP]
SPEAKER: Dialogue with [stage directions].

Begin script:"""


SUMMARY_PROMPT = """Summarize this podcast episode for use as callbacks in future episodes.

SCRIPT:
{script}

Create a 2-3 sentence summary that captures:
- Main topic discussed
- Any memorable moments or jokes
- Key conclusions or disagreements
- Something Doug or Claire said that could be referenced later

This will be used to create continuity in future episodes (e.g., "Remember last week when Doug said...").

Keep it concise and reference-friendly."""
