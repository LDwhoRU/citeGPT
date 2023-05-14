import os
import openai
import re
openai.api_key = os.getenv("OPENAI_API_KEY")

# reference - (Ryan & Deci, 2000)
# model = "gpt-4"
model = "gpt-3.5-turbo"

# Report handles the student report written by the student
class Report:
  def __init__(self, path="", text=""):
    # Provide path to report
    self.path = path
    # Otherwise use raw text input
    self.text = text

    # Convert file path to text
    if path:
      with open(path) as f:
        self.text = f.read()

  # Getter for raw student original text
  def get_text(self):
    return self.text

  # Rewrite student report based on findings supplied
  # Findings - List of all relevant findings identified
  def rewrite(self, findings, citation, output_terminal=False):
    concat_findings = "I have conducted research recently and discovered the following cool ideas and findings from a research paper I read:\n\n"
    for num, finding in enumerate(findings):
      concat_findings = concat_findings + str(num+1) + ": " + finding

    rewrite_prompt = "Using these findings, rewrite my report below, integrating the ideas and findings discovered from the research above. Do so in an extremely professional, academic, superb quality, that would be accepted in professional academia. Focus only on integrating my findings in a natural manner into the body of text.\n"
    citation_prompt = "A reminder that when referring to the findings I have supplied, utilise the in-text reference of the paper: " + citation + "\nThis must be done to ensure the paper is cited appropriately using the supplied in-text reference.\n"
    report_prompt = "My report is below:\n\n"

    question = concat_findings + "\n" + rewrite_prompt + citation_prompt + report_prompt + self.text

    completion = openai.ChatCompletion.create(
      model=model,
      messages=[
        {"role": "user", "content": question}
      ]
    )
    new_text = completion.choices[0].message.content

    if output_terminal:
      print(new_text)
    with open('output.txt', 'w') as f:
      f.write(new_text)

    return new_text