import os
import json
import re
import http.client

HEX_COLOR_RE = re.compile(r"^#([0-9A-Fa-f]{6})$")

EXAMPLES = """
Request:
Build me a SaaS landing page for my AI analytics product called InsightGen, \
with primary color #2A9D8F, a hero section, features list, and email sign-up form.

Spec:
{
  "template": "saas-landing",
  "brand": { "name": "InsightGen", "primaryColor": "#2A9D8F" },
  "sections": [
    { "type": "hero", "headline": "InsightGen AI Analytics", \
      "subhead": "Turn data into decisions", "cta": "Get Started" },
    { "type": "features", "items": ["Real-time dashboards", \
      "Predictive models", "Custom alerts"] },
    { "type": "signupForm", "fields": ["email"] }
  ]
}

Request:
Create a simple portfolio site for a photographer named Luna, \
primary color #E76F51, hero with title and subtitle, \
and a signup form collecting email and name.

Spec:
{
  "template": "portfolio",
  "brand": { "name": "Luna Photography", "primaryColor": "#E76F51" },
  "sections": [
    { "type": "hero", "headline": "Luna Photography", \
      "subhead": "Capturing moments one shot at a time", \
      "cta": "View Portfolio" },
    { "type": "signupForm", "fields": ["email", "name"] }
  ]
}
"""

def interpret_spec(user_request: str) -> dict:
    """
    Stubbed interpreter: for now just re-loads spec.json
    or you can wire in OpenAI later.
    """
    # **Simple pass-through**:  
    # if the user already specified spec.json, just return it:
    try:
        # if user_request exactly matches something in spec.json, return that
        return json.load(open("spec.json", encoding="utf-8"))
    except Exception:
        # Fallback minimal spec
        return {
            "template": "saas-landing",
            "brand": { "name": "InsightGen", "primaryColor": "#2A9D8F" },
            "sections": [
                {"type":"hero","headline":"InsightGen AI","subhead":"Data to Decisions","cta":"Get Started"},
                {"type":"features","items":[
                    {"title":"Real-Time Dashboards","description":"Live metrics."},
                    {"title":"Predictive Models","description":"Forecast trends."},
                    {"title":"Custom Alerts","description":"Be the first to know."}
                ]},
                {"type":"signupForm","fields":["email"]}
            ]
        }
