from openai import OpenAI
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
import os
import json
from typing import Dict, List, Tuple, Optional
from database import DocumentDB
from file_manager import FileManager

# Load environment variables and initialize clients
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
console = Console()
db = DocumentDB()
file_mgr = FileManager()

class CoverLetterGenerator:
    def __init__(self):
        # Load prompts from the database
        self.info_manager_prompt = self._load_prompt("info_manager")
        self.job_analyzer_prompt = self._load_prompt("job_analyzer")
        self.alignment_prompt = self._load_prompt("alignment")
        self.validator_prompt = self._load_prompt("validator")
        self.max_retries = 3

    def _load_prompt(self, name: str) -> str:
        """Load a prompt from the database."""
        prompt = db.get_prompt(name)
        if not prompt:
            raise ValueError(f"Prompt '{name}' not found in database. Please initialize prompts first.")
        return prompt["content"]

    def validate_response(self, response: str, expected_format: str = "") -> bool:
        """Validate if the response is proper and not an error message."""
        messages = [
            {"role": "system", "content": self.validator_prompt},
            {"role": "user", "content": f"""Please validate this response:

Response to validate:
{response}

Expected format (if any):
{expected_format}

Is this a valid, helpful response? Reply with exactly VALID or INVALID."""}
        ]

        try:
            validation_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            result = validation_response.choices[0].message.content.strip()
            return result == "VALID"
        except Exception:
            return False

    def get_completion_with_validation(self, messages: List[Dict[str, str]], model: str = "gpt-4o", expected_format: str = "") -> Tuple[bool, str]:
        """Get completion from OpenAI API with validation and retries."""
        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                result = response.choices[0].message.content

                # Validate the response
                if self.validate_response(result, expected_format):
                    return True, result
                
                console.print(f"[yellow]Attempt {attempt + 1}: Invalid response detected. Retrying...[/yellow]")
                continue

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return False, str(e)
                console.print(f"[yellow]Attempt {attempt + 1}: Error occurred. Retrying...[/yellow]")
                continue

        return False, "Failed to generate a valid response after multiple attempts"

    def process_user_info(self, resume: str, previous_letters: List[str], preferences: Optional[str] = None) -> str:
        """Stage 1: Process and organize user information."""
        letters_text = "\n---\n".join(previous_letters)
        preferences_text = f"\nPreferences:\n{preferences}" if preferences else ""
        
        content = f"""Please analyze the following information and provide a candidate profile:

Resume:
{resume}

Previous Cover Letters:
{letters_text}
{preferences_text}"""

        messages = [
            {"role": "system", "content": self.info_manager_prompt},
            {"role": "user", "content": content}
        ]

        success, response = self.get_completion_with_validation(
            messages, 
            model="gpt-4o",
            expected_format="""# Professional Profile
[Profile content]

# Key Qualifications
* [Qualifications]

# Experience Highlights
* [Highlights]

# Education & Certifications
* [Education details]"""
        )
        if success:
            return response
        return f"Error processing user information: {response}"

    def analyze_job(self, job_description: str) -> str:
        """Stage 2: Analyze job description."""
        content = f"""Please analyze the following job description:

{job_description}"""

        messages = [
            {"role": "system", "content": self.job_analyzer_prompt},
            {"role": "user", "content": content}
        ]

        success, response = self.get_completion_with_validation(
            messages, 
            model="gpt-4o",
            expected_format="""# Core Requirements
* [Requirements]

# Preferred Qualifications
* [Qualifications]

# Key Responsibilities
* [Responsibilities]"""
        )
        if success:
            return response
        return f"Error analyzing job: {response}"

    def align_profile_with_job(self, user_profile: str, job_analysis: str) -> str:
        """Stage 3: Match user profile with job requirements."""
        content = f"""Please analyze how well the candidate matches the job requirements:

Candidate Profile:
{user_profile}

Job Analysis:
{job_analysis}"""
        
        messages = [
            {"role": "system", "content": self.alignment_prompt},
            {"role": "user", "content": content}
        ]

        success, response = self.get_completion_with_validation(
            messages, 
            model="gpt-4o",
            expected_format="""# Key Matches
* [Matches]

# Areas to Address
* [Areas]

# Recommended Focus Points
* [Points]"""
        )
        if success:
            return response
        return f"Error in alignment: {response}"

    def generate_cover_letter(self, alignment_data: str, sample_letter: str) -> str:
        """Stage 4: Generate the final cover letter."""
        content = f"""You are a skilled professional writer. Generate a compelling, natural-sounding cover letter (about 300 words) that:
1. Uses the sample letter as a style guide for tone and format
2. Focuses on the key points identified in the alignment analysis
3. Tells a coherent story about why the candidate is an excellent fit
4. Addresses any potential concerns identified
5. Maintains a confident but humble tone

Alignment Analysis:
{alignment_data}

Sample Letter for Style:
{sample_letter}"""
        
        messages = [
            {"role": "user", "content": content}
        ]

        success, response = self.get_completion_with_validation(
            messages, 
            model="o1-preview",
            expected_format="[Professional letter format with clear paragraphs and standard business letter structure]"
        )
        if success:
            return response
        return f"Error generating cover letter: {response}"

    def process_biography_update(self, new_content: str, current_content: Optional[str], notes: str) -> str:
        """Process and merge biography updates."""
        content = f"""Please process this biographical information update:

New Content:
{new_content}

Current Content:
{current_content if current_content else 'No existing content'}

Notes:
{notes}

Please create a comprehensive, well-organized biography that:
1. {'Replaces the existing content entirely with information from the new content' if 'remove' in notes.lower() or 'replace' in notes.lower() else 'Merges the new information with existing content'}
2. Maintains a professional and consistent tone
3. Organizes information logically by topic/chronology
4. Preserves specific details, achievements, and metrics
5. Removes any redundant information
6. Formats the text in Markdown for readability"""

        messages = [
            {"role": "user", "content": content}
        ]

        success, response = self.get_completion_with_validation(
            messages, 
            model="gpt-4o",
            expected_format="[Well-formatted markdown biography with clear sections and professional tone]"
        )
        if success:
            return response
        return f"Error processing biography update: {response}"

class CoverLetterEditor:
    def __init__(self):
        self.chat_history = []
        self.current_model = "gpt-4o"  # Default model
        self.system_prompt = """You are an expert cover letter editor. Help the user improve their cover letter through a natural conversation.
Your goal is to make the cover letter more compelling, clear, and tailored to the job while maintaining the user's voice.
You can suggest improvements to:
- Structure and flow
- Language and tone
- Content and emphasis
- Specific phrases or sentences
Be constructive and explain your suggestions clearly."""
    
    def start_editing_session(self, cover_letter: str) -> None:
        """Start a new editing session with the given cover letter."""
        self.chat_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "I'm here to help you edit your cover letter. What would you like me to help you with?"}
        ]
        
        # Display the cover letter
        console.print("\n[green]Current Cover Letter:[/green]")
        console.print(Markdown(cover_letter))
        
        # Store the cover letter in an instance variable for reference
        self.current_letter = cover_letter
    
    def process_message(self, message: str) -> None:
        """Process a user message and get AI response."""
        # Check for model switch command
        if message.startswith("\\4o") or message.startswith("\\o1"):
            new_model = "gpt-4o" if message.startswith("\\4o") else "o1-preview"
            message = message[3:].strip()  # Remove the model switch prefix
            if not message:  # If only model switch command, just switch model
                self.current_model = new_model
                console.print(f"[yellow]Switched to {new_model} model[/yellow]")
                return
            self.current_model = new_model
        
        # Add context about the cover letter if this is the first user message
        if len(self.chat_history) == 2:  # Only system prompt and initial assistant message
            message = f"Here's my cover letter:\n\n{self.current_letter}\n\n{message}"
        
        # Add user message to history
        self.chat_history.append({"role": "user", "content": message})
        
        try:
            # Get AI response
            response = client.chat.completions.create(
                model=self.current_model,
                messages=self.chat_history
            )
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Display response
            console.print("\n[green]AI Editor:[/green]")
            console.print(Markdown(ai_response))
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            # Remove the failed message from history
            self.chat_history.pop()

def display_documents(doc_type: str):
    """Display a table of documents of the specified type."""
    docs = db.list_documents(doc_type)
    
    table = Table(title=f"{doc_type.replace('_', ' ').title()}")
    table.add_column("Name")
    table.add_column("Created At")
    if doc_type == "job_description":
        table.add_column("Company")
        table.add_column("Position")
        
    for doc in docs:
        if doc_type == "job_description":
            table.add_row(doc["name"], doc["created_at"], doc["company"], doc["position"])
        else:
            table.add_row(doc["name"], doc["created_at"])
    
    console.print(table)

def import_document(doc_type: str):
    """Import a document from file or manual input."""
    import_type = Prompt.ask("Import from [1] file or [2] paste content", choices=["1", "2"])
    
    name = Prompt.ask(f"Enter a name for this {doc_type.replace('_', ' ')}")
    content = ""
    
    if import_type == "1":
        file_path = Prompt.ask("Enter the path to your file (supports .txt, .pdf, .md, .json, .yaml, .html)")
        
        # Check file type and validity
        is_valid, file_type, error_msg = file_mgr.get_file_info(file_path)
        if not is_valid:
            console.print(f"[red]{error_msg}[/red]")
            return False
            
        console.print(f"[yellow]Reading {file_type.upper()} file...[/yellow]")
        content = file_mgr.import_file(file_path)
        
        if not content:
            console.print(f"[red]Failed to read file: {file_path}[/red]")
            return False
            
        if file_type == "pdf":
            console.print("[green]Successfully extracted text from PDF[/green]")
    else:
        console.print(f"\nEnter/paste your {doc_type.replace('_', ' ')} content (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            content = "\n".join(lines)
    
    if not content.strip():
        console.print("[red]Error: Empty content is not allowed[/red]")
        return False
    
    metadata = {}
    if doc_type == "job_description":
        metadata["company"] = Prompt.ask("Enter company name")
        metadata["position"] = Prompt.ask("Enter position title")
    
    # Save to database first
    console.print("[yellow]Saving to database...[/yellow]")
    if not db.save_document(doc_type, name, content, metadata):
        console.print("[red]Failed to save document to database[/red]")
        return False
    
    # Then save to file system
    console.print("[yellow]Saving to file system...[/yellow]")
    file_path = file_mgr.write_file(doc_type, name, content)
    if not file_path:
        console.print("[red]Failed to save document to file system[/red]")
        # Consider rolling back the database save here
        if db.delete_document(doc_type, name):
            console.print("[yellow]Rolled back database save due to file system error[/yellow]")
        return False
    
    console.print(f"\n[green]Successfully imported {doc_type.replace('_', ' ')}![/green]")
    console.print(f"[green]Saved to: {file_path}[/green]")
    return True

def select_document(doc_type: str) -> Optional[Dict]:
    """Select a document from the available ones."""
    docs = db.list_documents(doc_type)
    if not docs:
        console.print(f"\n[yellow]No {doc_type.replace('_', ' ')}s found![/yellow]")
        return None
    
    display_documents(doc_type)
    
    # Create numbered choices
    choices = {str(i+1): doc["name"] for i, doc in enumerate(docs)}
    
    # Display numbered options
    console.print("\nAvailable options:")
    for num, name in choices.items():
        console.print(f"{num}: {name}")
    
    choice = Prompt.ask("\nSelect option", choices=list(choices.keys()))
    selected_name = choices[choice]
    
    return db.get_document(doc_type, selected_name)

def main_menu():
    """Display and handle the main menu."""
    while True:
        console.print("\n=== Cover Letter Generator ===")
        console.print("1. Manage Resumes")
        console.print("2. Manage Cover Letters")
        console.print("3. Manage Job Descriptions")
        console.print("4. Manage Biography")
        console.print("5. Generate Cover Letter")
        console.print("6. Edit Cover Letter")
        console.print("7. Settings")
        console.print("8. Exit")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "8":
            break
            
        if choice in ["1", "2", "3"]:
            doc_type = {
                "1": "resume",
                "2": "cover_letter",
                "3": "job_description"
            }[choice]
            
            console.print(f"\n=== {doc_type.replace('_', ' ').title()} Management ===")
            console.print("1. List documents")
            console.print("2. Import new document")
            console.print("3. Delete document")
            console.print("4. Back to main menu")
            
            sub_choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            
            if sub_choice == "1":
                display_documents(doc_type)
            elif sub_choice == "2":
                import_document(doc_type)
            elif sub_choice == "3":
                doc = select_document(doc_type)
                if doc and Confirm.ask(f"Are you sure you want to delete {doc['name']}?"):
                    db.delete_document(doc_type, doc["name"])
                    file_mgr.delete_file(doc_type, doc["name"])
                    console.print("[green]Document deleted successfully![/green]")
        
        elif choice == "4":
            console.print("\n=== Biography Management ===")
            console.print("1. View current biography")
            console.print("2. Add/Update information")
            console.print("3. View version history")
            console.print("4. Manage versions/Delete")
            console.print("5. Back to main menu")
            
            sub_choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            
            if sub_choice == "1":
                current_bio = db.get_biography()
                if current_bio:
                    console.print("\n[green]Current Biography:[/green]")
                    console.print(Markdown(current_bio["content"]))
                else:
                    console.print("[yellow]No biography found. Please add information.[/yellow]")
            
            elif sub_choice == "2":
                # Get current biography if it exists
                current_bio = db.get_biography()
                current_content = current_bio["content"] if current_bio else None
                
                # Get new content
                import_type = Prompt.ask("Import from [1] file or [2] paste content", choices=["1", "2"])
                new_content = ""
                
                if import_type == "1":
                    file_path = Prompt.ask("Enter the path to your file")
                    is_valid, file_type, error_msg = file_mgr.get_file_info(file_path)
                    if not is_valid:
                        console.print(f"[red]{error_msg}[/red]")
                        continue
                    
                    new_content = file_mgr.import_file(file_path)
                    if not new_content:
                        console.print("[red]Failed to read file[/red]")
                        continue
                else:
                    console.print("\nEnter/paste your content (press Ctrl+D or Ctrl+Z when done):")
                    lines = []
                    try:
                        while True:
                            line = input()
                            lines.append(line)
                    except EOFError:
                        new_content = "\n".join(lines)
                
                if not new_content.strip():
                    console.print("[red]Error: Empty content is not allowed[/red]")
                    continue
                
                # Get notes about the update
                notes = Prompt.ask("Enter any notes about this update (optional)", default="")
                
                # Process and merge the new information
                generator = CoverLetterGenerator()
                updated_bio = generator.process_biography_update(new_content, current_content, notes)
                
                if updated_bio.startswith("Error"):
                    console.print(f"[red]{updated_bio}[/red]")
                    continue
                
                # Save the new version
                if db.save_biography(updated_bio, notes):
                    console.print("[green]Biography updated successfully![/green]")
                    
                    # Also save to file system
                    version_info = db.get_biography()  # Get the latest version
                    if version_info:
                        file_path = file_mgr.write_file("biography", f"version_{version_info['version']}", updated_bio)
                        if file_path:
                            console.print(f"[green]Saved to: {file_path}[/green]")
                else:
                    console.print("[red]Failed to update biography[/red]")
            
            elif sub_choice == "3":
                versions = db.list_biography_versions()
                if versions:
                    table = Table(title="Biography Versions")
                    table.add_column("Version")
                    table.add_column("Created At")
                    table.add_column("Notes")
                    
                    for version in versions:
                        table.add_row(
                            str(version["version"]),
                            version["created_at"],
                            version["notes"] or ""
                        )
                    
                    console.print(table)
                else:
                    console.print("[yellow]No biography versions found[/yellow]")
            
            elif sub_choice == "4":
                console.print("\n=== Manage Biography Versions ===")
                console.print("1. Revert to previous version")
                console.print("2. Delete current biography")
                console.print("3. Back")
                
                version_choice = Prompt.ask("Select an option", choices=["1", "2", "3"])
                
                if version_choice == "1":
                    versions = db.list_biography_versions()
                    if not versions:
                        console.print("[yellow]No biography versions found[/yellow]")
                        continue
                    
                    # Display versions
                    table = Table(title="Biography Versions")
                    table.add_column("Version")
                    table.add_column("Created At")
                    table.add_column("Notes")
                    
                    for version in versions:
                        table.add_row(
                            str(version["version"]),
                            version["created_at"],
                            version["notes"] or ""
                        )
                    
                    console.print(table)
                    
                    # Get version to revert to
                    version_num = Prompt.ask("Enter version number to revert to", choices=[str(v["version"]) for v in versions])
                    if Confirm.ask(f"Are you sure you want to revert to version {version_num}?"):
                        old_version = db.get_biography(int(version_num))
                        if old_version:
                            if db.save_biography(old_version["content"], f"Reverted to version {version_num}"):
                                console.print(f"[green]Successfully reverted to version {version_num}[/green]")
                            else:
                                console.print(f"[red]Failed to revert to version {version_num}[/red]")
                        else:
                            console.print(f"[red]Failed to retrieve version {version_num}[/red]")
                
                elif version_choice == "2":
                    if Confirm.ask("Are you sure you want to delete the current biography? This action cannot be undone."):
                        if db.delete_biography():
                            console.print("[green]Biography deleted successfully![/green]")
                        else:
                            console.print("[red]Failed to delete biography[/red]")
        
        elif choice == "6":
            # Select cover letter to edit
            cover_letter_doc = select_document("cover_letter")
            if not cover_letter_doc:
                console.print("[red]Please import a cover letter first![/red]")
                continue
            
            # Start editing session
            editor = CoverLetterEditor()
            editor.start_editing_session(cover_letter_doc["content"])
            
            console.print("\n[yellow]Enter your messages to edit the cover letter.[/yellow]")
            console.print("[yellow]Use \\4o or \\o1 at the start of a message to switch AI models.[/yellow]")
            console.print("[yellow]Type 'exit' to end the editing session.[/yellow]\n")
            
            while True:
                message = Prompt.ask("You")
                if message.lower() == 'exit':
                    break
                
                editor.process_message(message)
            
            if Confirm.ask("Would you like to save the edited cover letter?"):
                name = Prompt.ask("Enter a name for this cover letter")
                
                # Get the final version from chat history
                final_content = ""
                for msg in reversed(editor.chat_history):
                    if "cover letter" in msg["content"].lower():
                        final_content = msg["content"]
                        break
                
                if final_content:
                    db.save_document("cover_letter", name, final_content)
                    file_mgr.write_file("cover_letter", name, final_content)
                    console.print("[green]Cover letter saved successfully![/green]")
                else:
                    console.print("[red]Could not find final version in chat history.[/red]")
                    console.print("[yellow]Please copy and save the final version manually.[/yellow]")

        elif choice == "7":
            console.print("\n=== Settings ===")
            console.print("1. Manage AI Prompts")
            console.print("2. Back to main menu")
            
            settings_choice = Prompt.ask("Select an option", choices=["1", "2"])
            
            if settings_choice == "1":
                console.print("\n=== AI Prompt Management ===")
                console.print("1. List prompts")
                console.print("2. View prompt")
                console.print("3. Edit prompt")
                console.print("4. Reset to default")
                console.print("5. Back")
                
                prompt_choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
                
                if prompt_choice == "1":
                    prompts = db.list_prompts()
                    if prompts:
                        table = Table(title="AI Prompts")
                        table.add_column("Name")
                        table.add_column("Description")
                        table.add_column("Last Updated")
                        
                        for prompt in prompts:
                            table.add_row(
                                prompt["name"],
                                prompt["description"] or "",
                                prompt["updated_at"]
                            )
                        
                        console.print(table)
                    else:
                        console.print("[yellow]No prompts found. Use 'Reset to default' to initialize prompts.[/yellow]")
                
                elif prompt_choice == "2":
                    prompts = db.list_prompts()
                    if not prompts:
                        console.print("[yellow]No prompts found. Use 'Reset to default' to initialize prompts.[/yellow]")
                        continue
                    
                    # Create numbered choices
                    choices = {str(i+1): prompt["name"] for i, prompt in enumerate(prompts)}
                    
                    # Display numbered options
                    console.print("\nAvailable prompts:")
                    for num, name in choices.items():
                        console.print(f"{num}: {name}")
                    
                    choice = Prompt.ask("\nSelect prompt", choices=list(choices.keys()))
                    selected_name = choices[choice]
                    
                    prompt = db.get_prompt(selected_name)
                    if prompt:
                        console.print(f"\n[green]Prompt: {prompt['name']}[/green]")
                        if prompt["description"]:
                            console.print(f"[blue]Description: {prompt['description']}[/blue]")
                        console.print("\n[white]Content:[/white]")
                        console.print(prompt["content"])
                
                elif prompt_choice == "3":
                    prompts = db.list_prompts()
                    if not prompts:
                        console.print("[yellow]No prompts found. Use 'Reset to default' to initialize prompts.[/yellow]")
                        continue
                    
                    # Create numbered choices
                    choices = {str(i+1): prompt["name"] for i, prompt in enumerate(prompts)}
                    
                    # Display numbered options
                    console.print("\nAvailable prompts:")
                    for num, name in choices.items():
                        console.print(f"{num}: {name}")
                    
                    choice = Prompt.ask("\nSelect prompt to edit", choices=list(choices.keys()))
                    selected_name = choices[choice]
                    
                    prompt = db.get_prompt(selected_name)
                    if prompt:
                        console.print(f"\n[green]Editing prompt: {prompt['name']}[/green]")
                        console.print("[yellow]Current content:[/yellow]")
                        console.print(prompt["content"])
                        
                        console.print("\nEnter new content (press Ctrl+D or Ctrl+Z when done):")
                        lines = []
                        try:
                            while True:
                                line = input()
                                lines.append(line)
                        except EOFError:
                            new_content = "\n".join(lines)
                        
                        if new_content.strip():
                            description = Prompt.ask("Enter prompt description (optional)", default=prompt["description"] or "")
                            if db.save_prompt(selected_name, new_content, description):
                                console.print("[green]Prompt updated successfully![/green]")
                                # Also save to file system
                                file_mgr.write_file("prompts", selected_name, new_content)
                            else:
                                console.print("[red]Failed to update prompt[/red]")
                
                elif prompt_choice == "4":
                    if Confirm.ask("This will reset all prompts to their default values. Continue?"):
                        # Initialize default prompts
                        default_prompts = {
                            "info_manager": {
                                "content": CoverLetterGenerator().info_manager_prompt,
                                "description": "Analyzes resumes and biographical information"
                            },
                            "job_analyzer": {
                                "content": CoverLetterGenerator().job_analyzer_prompt,
                                "description": "Analyzes job descriptions"
                            },
                            "alignment": {
                                "content": CoverLetterGenerator().alignment_prompt,
                                "description": "Matches candidates with job requirements"
                            },
                            "validator": {
                                "content": CoverLetterGenerator().validator_prompt,
                                "description": "Validates AI responses"
                            }
                        }
                        
                        for name, data in default_prompts.items():
                            if db.save_prompt(name, data["content"], data["description"]):
                                file_mgr.write_file("prompts", name, data["content"])
                        
                        console.print("[green]Prompts reset to default values![/green]")

        elif choice == "5":
            # Select resume
            resume_doc = select_document("resume")
            if not resume_doc:
                console.print("[red]Please import a resume first![/red]")
                continue
            
            # Select sample cover letter for style
            sample_letter_doc = select_document("cover_letter")
            if not sample_letter_doc:
                console.print("[red]Please import a sample cover letter first![/red]")
                continue
            
            # Select job description
            job_doc = select_document("job_description")
            if not job_doc:
                console.print("[red]Please import a job description first![/red]")
                continue
            
            # Get preferences
            preferences = Prompt.ask("Enter any specific preferences (tone, style, etc.)", default="")
            
            # Generate cover letter
            generator = CoverLetterGenerator()
            
            # Get current biography
            current_bio = db.get_biography()
            if current_bio:
                console.print("[yellow]Using information from your biography...[/yellow]")
            
            console.print("\n[yellow]Processing your information...[/yellow]")
            user_profile = generator.process_user_info(
                resume_doc["content"],
                [sample_letter_doc["content"]],
                f"{preferences}\n\nBiography:\n{current_bio['content'] if current_bio else ''}"
            )
            if user_profile.startswith("Error"):
                console.print(f"[red]{user_profile}[/red]")
                continue

            console.print("\n[green]Candidate Profile:[/green]")
            console.print(Markdown(user_profile))

            console.print("\n[yellow]Analyzing job description...[/yellow]")
            job_analysis = generator.analyze_job(job_doc["content"])
            if job_analysis.startswith("Error"):
                console.print(f"[red]{job_analysis}[/red]")
                continue

            console.print("\n[green]Job Analysis:[/green]")
            console.print(Markdown(job_analysis))

            console.print("\n[yellow]Matching your profile with job requirements...[/yellow]")
            alignment = generator.align_profile_with_job(user_profile, job_analysis)
            if alignment.startswith("Error"):
                console.print(f"[red]{alignment}[/red]")
                continue

            console.print("\n[green]Profile Alignment:[/green]")
            console.print(Markdown(alignment))

            console.print("\n[yellow]Generating your cover letter...[/yellow]")
            cover_letter = generator.generate_cover_letter(alignment, sample_letter_doc["content"])
            if cover_letter.startswith("Error"):
                console.print(f"[red]{cover_letter}[/red]")
                continue
            
            # Save the generated cover letter
            name = Prompt.ask("Enter a name for this cover letter")
            db.save_document("cover_letter", name, cover_letter)
            file_mgr.write_file("cover_letter", name, cover_letter)
            
            console.print("\n[green]Here's your generated cover letter:[/green]\n")
            console.print(Markdown(cover_letter))

def initialize_default_prompts():
    """Initialize the default prompts in the database if they don't exist."""
    default_prompts = {
        "info_manager": {
            "content": '''You are an expert at analyzing resumes, cover letters, and biographical information to extract key insights about a candidate.

Input includes:
- Resume in plain text
- Previous cover letters
- Optional notes about preferences (tone, keywords, etc.)
- Biography (if available)

Analyze the input and provide a clear, organized summary of the candidate's profile in this format:

# Professional Profile
[A concise paragraph highlighting the candidate's current focus, key strengths, and unique value proposition]

# Key Qualifications
* [List the most relevant and impressive qualifications, skills, and achievements]
* [Focus on concrete accomplishments with metrics when available]
* [Include technical skills, soft skills, and domain expertise]

# Experience Highlights
* [List the most relevant experience points for the context]
* [Focus on achievements and impact rather than just responsibilities]
* [Include specific technologies, methodologies, or approaches used]

# Education & Certifications
* [List relevant education and certifications with dates]
* [Include notable coursework or academic achievements if relevant]

# Additional Insights
* [Any other relevant information about work style, preferences, or special qualifications]
* [Note any recurring themes or strengths from cover letters]
* [Include any specific preferences mentioned]

Important:
- Focus on quality over quantity
- Be specific and concrete, avoid vague statements
- Preserve actual metrics and achievements from the source material
- Don't make assumptions or fill in gaps
- If something is uncertain, either omit it or clearly indicate the uncertainty''',
            "description": "Analyzes resumes and biographical information"
        },
        "job_analyzer": {
            "content": '''You are an expert at analyzing job descriptions to identify key requirements and success factors.

Analyze the job description and provide a clear, organized breakdown in this format:

# Core Requirements
* [List the absolute must-have qualifications]
* [Include specific technical skills required]
* [Note years of experience or education requirements]

# Preferred Qualifications
* [List the "nice-to-have" qualifications]
* [Include bonus skills or experiences]

# Key Responsibilities
* [List the main duties and expectations]
* [Focus on what success looks like in this role]

# Company & Culture
* [Describe the company values and culture based on the description]
* [Note any specific work environment details]

# Writing Style Guide
* Tone: [Analyze the job description's tone - formal, casual, enthusiastic, etc.]
* Keywords: [List important terms and phrases used repeatedly]
* Style Notes: [Any other notable aspects of the writing style]

Important:
- Distinguish clearly between required and preferred qualifications
- Preserve specific technical terms and industry jargon
- Note any unique or standout requirements
- Don't make assumptions about unlisted requirements''',
            "description": "Analyzes job descriptions"
        },
        "alignment": {
            "content": '''You are an expert at matching candidates with job requirements and crafting compelling narratives.

Your task is to analyze how well a candidate's profile matches a job's requirements and identify the most compelling points to emphasize.

Review the candidate profile and job analysis, then provide:

# Key Matches
* [List the strongest matches between the candidate and job requirements]
* [Include specific examples and achievements that demonstrate each match]
* [Note any unique qualifications that set the candidate apart]

# Areas to Address
* [List any gaps or weaker matches]
* [Suggest ways to address or reframe these areas]
* [Note any compensating strengths that could offset gaps]

# Recommended Focus Points
* [List 3-4 key points that should be emphasized in the cover letter]
* [Include specific achievements or experiences to highlight]
* [Note any unique angles or connections to emphasize]

# Suggested Approach
* [Recommend a specific tone or style for the letter]
* [Note any company values or themes to weave in]
* [Suggest any specific experiences to elaborate on]

Important:
- Focus on the strongest and most relevant matches
- Be specific about how experiences demonstrate required skills
- Suggest concrete ways to address any gaps
- Consider both technical and cultural fit''',
            "description": "Matches candidates with job requirements"
        },
        "validator": {
            "content": '''You are a response validator for an AI system. Your job is to check if a response is valid and helpful, or if it's an error message or non-helpful response.

Rules for validation:
1. Response should be relevant and on-topic
2. Response should not contain phrases like "I can't help", "I'm sorry", "I cannot assist"
3. Response should not be empty or contain only generic statements
4. Response should follow the expected format for the given task

Return exactly "VALID" if the response is good, or "INVALID" if the response contains errors or non-helpful content.''',
            "description": "Validates AI responses"
        }
    }
    
    # Save prompts to database and file system
    for name, data in default_prompts.items():
        if db.save_prompt(name, data["content"], data["description"]):
            file_mgr.write_file("prompts", name, data["content"])

if __name__ == "__main__":
    # Initialize prompts if they don't exist
    if not db.list_prompts():
        initialize_default_prompts()
    main_menu() 