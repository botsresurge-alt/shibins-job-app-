import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# Set your Gemini API key here
genai.configure(api_key="AIzaSyCPogoDORa439bzLCA_7Ph8dnh8X1PoB2o")

def scrape_linkedin(linkedin_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(linkedin_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        headline = soup.find("h2", {"class": "text-heading-xlarge"}).get_text(strip=True) if soup.find("h2", {"class": "text-heading-xlarge"}) else ""
        about = soup.find("div", {"class": "pv-shared-text-with-see-more"}).get_text(strip=True) if soup.find("div", {"class": "pv-shared-text-with-see-more"}) else ""
        return {"headline": headline, "about": about}
    except Exception as e:
        print(f"Could not scrape LinkedIn: {e}")
        return {}

def get_job_suggestions(user_details):
    prompt = (
        f"User Details:\n"
        f"Name: {user_details['name']}\n"
        f"Education: {user_details['education']}\n"
        f"Skills: {user_details['skills']}\n"
        f"Interests: {user_details['interests']}\n"
    )
    if user_details.get("linkedin"):
        prompt += f"LinkedIn Headline: {user_details['linkedin'].get('headline', '')}\n"
        prompt += f"LinkedIn About: {user_details['linkedin'].get('about', '')}\n"
    prompt += "Suggest suitable job roles for this user and format the result nicely."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[b][color=ff0000]Error:[/color][/b] {e}"

class JobSuggestionApp(App):
    def build(self):
        self.title = "Job Suggestion Generator"
        main_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Input fields
        self.name_input = TextInput(hint_text="Enter your Name", multiline=False, size_hint_y=None, height=40)
        self.education_input = TextInput(hint_text="Enter your Education", multiline=False, size_hint_y=None, height=40)
        self.skills_input = TextInput(hint_text="Enter your Skills (comma separated)", multiline=False, size_hint_y=None, height=40)
        self.interests_input = TextInput(hint_text="Enter your Interests (comma separated)", multiline=False, size_hint_y=None, height=40)
        self.linkedin_input = TextInput(hint_text="Enter your LinkedIn URL (optional)", multiline=False, size_hint_y=None, height=40)

        main_layout.add_widget(Label(text="[b]Job Suggestion Generator[/b]", markup=True, font_size=24, size_hint_y=None, height=50))
        main_layout.add_widget(self.name_input)
        main_layout.add_widget(self.education_input)
        main_layout.add_widget(self.skills_input)
        main_layout.add_widget(self.interests_input)
        main_layout.add_widget(self.linkedin_input)

        # Generate button
        generate_btn = Button(text="Generate Suggestions", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.8, 1))
        generate_btn.bind(on_press=self.on_generate)
        main_layout.add_widget(generate_btn)

        # Output area
        self.output_label = Label(text="", markup=True, font_size=16, size_hint_y=None)
        self.output_scroll = ScrollView(size_hint=(1, 1))
        self.output_scroll.add_widget(self.output_label)
        main_layout.add_widget(self.output_scroll)

        return main_layout

    def on_generate(self, instance):
        name = self.name_input.text.strip()
        education = self.education_input.text.strip()
        skills = self.skills_input.text.strip()
        interests = self.interests_input.text.strip()
        linkedin_url = self.linkedin_input.text.strip()

        user_details = {
            "name": name,
            "education": education,
            "skills": skills,
            "interests": interests
        }
        if linkedin_url:
            user_details["linkedin"] = scrape_linkedin(linkedin_url)

        suggestions = get_job_suggestions(user_details)
        formatted = self.format_output(suggestions)
        self.output_label.text = formatted
        self.output_label.texture_update()
        self.output_label.height = self.output_label.texture_size[1]

    def format_output(self, suggestions):
        # Format output with bold headers and bullet points
        import re
        lines = suggestions.splitlines()
        formatted = "[b][color=228B22]=== Job Suggestions ===[/color][/b]\n\n"
        for line in lines:
            match = re.match(r"[\d\-\*\.]+\s*(.+)", line)
            if match:
                formatted += f"• {match.group(1).strip()}\n"
            elif line.strip() and not line.lower().startswith("user details"):
                formatted += f"• {line.strip()}\n"
        formatted += "\n[b][color=228B22]=======================[/color][/b]"
        return formatted

if __name__ == "__main__":
    JobSuggestionApp().run()
