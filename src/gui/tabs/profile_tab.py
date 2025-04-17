import customtkinter
import json
import os
from tkinter import messagebox

class ProfileTab(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Load user data
        self.user_data = self.load_user_data()
        
        # Create sections
        self.sections = {}
        self.create_sections()
        
        # Add button for new sections
        self.add_section_button = customtkinter.CTkButton(
            self.scrollable_frame,
            text="Add New Section",
            command=self.add_new_section
        )
        self.add_section_button.grid(row=len(self.sections), column=0, padx=20, pady=20, sticky="ew")
        
        # Save button
        self.save_button = customtkinter.CTkButton(
            self.scrollable_frame,
            text="Save Profile",
            command=self.save_profile
        )
        self.save_button.grid(row=len(self.sections) + 1, column=0, padx=20, pady=20, sticky="ew")
        
    def load_user_data(self):
        """Load user data from user.json."""
        user_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config", "user.json")
        try:
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    return json.load(f)
            return {
                "personal_info": {},
                "eligibility": {},
                "demographics": {},
                "skills": [],
                "experiences": [],
                "education": [],
                "certifications": [],
                "languages": [],
                "special_instructions": []
            }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
            return {}
            
    def create_sections(self):
        """Create sections for each part of the profile."""
        # Standard sections
        sections = [
            ("Personal Info", "personal_info", self.create_personal_info_section),
            ("Eligibility", "eligibility", self.create_eligibility_section),
            ("Demographics", "demographics", self.create_demographics_section),
            ("Skills", "skills", self.create_skills_section),
            ("Experience", "experiences", self.create_experience_section),
            ("Education", "education", self.create_education_section),
            ("Certifications", "certifications", self.create_certifications_section),
            ("Languages", "languages", self.create_languages_section),
            ("Special Instructions", "special_instructions", self.create_special_instructions_section)
        ]
        
        # Add user-created sections
        for key in self.user_data:
            if key not in [s[1] for s in sections]:
                sections.append((key.replace("_", " ").title(), key, self.create_custom_section))
        
        for i, (title, key, create_func) in enumerate(sections):
            section = customtkinter.CTkFrame(self.scrollable_frame)
            section.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
            section.grid_columnconfigure(0, weight=1)
            
            label = customtkinter.CTkLabel(section, text=title, font=("Arial", 14, "bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Delete button for section
            delete_button = customtkinter.CTkButton(section, text="Delete Section", command=lambda k=key, s=section: self.delete_section(k, s))
            delete_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            
            content = create_func(section, key)
            content.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            
            self.sections[key] = content
            
    def create_custom_section(self, parent, key):
        """Create a custom section for user-defined data."""
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Custom section items
        items = self.user_data.get(key, [])
        self.custom_items = getattr(self, f"{key}_items", [])
        setattr(self, f"{key}_items", self.custom_items)
        
        for i, item in enumerate(items):
            item_frame = customtkinter.CTkFrame(frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Content
            customtkinter.CTkLabel(item_frame, text="Content:").grid(row=0, column=0, sticky="w", padx=5)
            content_text = customtkinter.CTkTextbox(item_frame, height=100)
            content_text.insert("1.0", item)
            content_text.grid(row=0, column=1, sticky="ew", padx=5)
            
            self.custom_items.append({
                "content": content_text
            })
            
        # Add new item button
        add_button = customtkinter.CTkButton(
            frame,
            text=f"Add {key.replace('_', ' ').title()}",
            command=lambda: self.add_custom_item(key)
        )
        add_button.grid(row=len(items), column=0, sticky="ew", padx=5, pady=5)
        setattr(self, f"{key}_add_button", add_button)
        
        return frame
        
    def add_custom_item(self, key):
        """Add a new item to a custom section."""
        items = getattr(self, f"{key}_items", [])
        add_button = getattr(self, f"{key}_add_button")
        
        item_frame = customtkinter.CTkFrame(self.sections[key])
        item_frame.grid(row=len(items), column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Content
        customtkinter.CTkLabel(item_frame, text="Content:").grid(row=0, column=0, sticky="w", padx=5)
        content_text = customtkinter.CTkTextbox(item_frame, height=100)
        content_text.grid(row=0, column=1, sticky="ew", padx=5)
        
        items.append({
            "content": content_text
        })
        
        # Move add button down
        add_button.grid(row=len(items), column=0, sticky="ew", padx=5, pady=5)
        
    def create_personal_info_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("Name", "name"),
            ("Address", "address"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("LinkedIn", "linkedin"),
            ("Website", "website"),
            ("GitHub", "github")
        ]
        
        for i, (label, field_key) in enumerate(fields):
            customtkinter.CTkLabel(frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = customtkinter.CTkEntry(frame)
            entry.insert(0, self.user_data.get("personal_info", {}).get(field_key, ""))
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            setattr(self, f"personal_info_{field_key}", entry)
            
        return frame
        
    def create_eligibility_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("Work Eligibility", "work_eligibility"),
            ("Visa Sponsorship Needed", "visa_sponsorship_needed"),
            ("Security Clearance", "security_clearance"),
            ("Willing to Relocate", "willing_to_relocate"),
            ("Willing to Travel", "willing_to_travel")
        ]
        
        for i, (label, field_key) in enumerate(fields):
            customtkinter.CTkLabel(frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = customtkinter.CTkEntry(frame)
            entry.insert(0, self.user_data.get("eligibility", {}).get(field_key, ""))
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            setattr(self, f"eligibility_{field_key}", entry)
            
        return frame
        
    def create_demographics_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("Gender", "gender"),
            ("Race/Ethnicity", "race_ethnicity"),
            ("Veteran Status", "veteran_status"),
            ("Disability Status", "disability_status"),
            ("Preferred Pronouns", "preferred_pronouns")
        ]
        
        for i, (label, field_key) in enumerate(fields):
            customtkinter.CTkLabel(frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = customtkinter.CTkEntry(frame)
            entry.insert(0, self.user_data.get("demographics", {}).get(field_key, ""))
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            setattr(self, f"demographics_{field_key}", entry)
            
        return frame
        
    def create_skills_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Skills list
        skills_list = customtkinter.CTkTextbox(frame, height=100)
        skills_list.insert("1.0", "\n".join(self.user_data.get("skills", [])))
        skills_list.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        setattr(self, "skills_textbox", skills_list)
        
        return frame
        
    def create_experience_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Experience items
        experiences = self.user_data.get("experiences", [])
        self.experience_items = []
        
        for i, exp in enumerate(experiences):
            item_frame = customtkinter.CTkFrame(frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Company
            customtkinter.CTkLabel(item_frame, text="Company:").grid(row=0, column=0, sticky="w", padx=5)
            company_entry = customtkinter.CTkEntry(item_frame)
            company_entry.insert(0, exp.get("company", ""))
            company_entry.grid(row=0, column=1, sticky="ew", padx=5)
            
            # Role
            customtkinter.CTkLabel(item_frame, text="Role:").grid(row=1, column=0, sticky="w", padx=5)
            role_entry = customtkinter.CTkEntry(item_frame)
            role_entry.insert(0, exp.get("role", ""))
            role_entry.grid(row=1, column=1, sticky="ew", padx=5)
            
            # Dates
            customtkinter.CTkLabel(item_frame, text="Dates:").grid(row=2, column=0, sticky="w", padx=5)
            dates_entry = customtkinter.CTkEntry(item_frame)
            dates_entry.insert(0, exp.get("dates", ""))
            dates_entry.grid(row=2, column=1, sticky="ew", padx=5)
            
            # Bullets
            customtkinter.CTkLabel(item_frame, text="Bullets:").grid(row=3, column=0, sticky="w", padx=5)
            bullets_text = customtkinter.CTkTextbox(item_frame, height=100)
            bullets_text.insert("1.0", "\n".join(exp.get("bullets", [])))
            bullets_text.grid(row=3, column=1, sticky="ew", padx=5)
            
            # Delete button
            delete_button = customtkinter.CTkButton(item_frame, text="Delete Experience", command=lambda f=item_frame: self.delete_experience_item(f))
            delete_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            
            self.experience_items.append({
                "frame": item_frame,
                "company": company_entry,
                "role": role_entry,
                "dates": dates_entry,
                "bullets": bullets_text
            })
        
        # Add new experience button
        add_button = customtkinter.CTkButton(
            frame,
            text="Add Experience",
            command=self.add_experience
        )
        add_button.grid(row=len(experiences), column=0, sticky="ew", padx=5, pady=5)
        
        return frame
        
    def delete_experience_item(self, item_frame):
        """Delete an experience item."""
        # Find the item in the list
        for i, item in enumerate(self.experience_items):
            if item["frame"] == item_frame:
                # Remove from the list
                self.experience_items.pop(i)
                # Destroy the frame
                item_frame.destroy()
                # Reposition remaining items
                for j in range(i, len(self.experience_items)):
                    self.experience_items[j]["frame"].grid(row=j)
                # Move add button down
                self.sections["experiences"].grid_slaves(row=len(self.experience_items))[0].grid(row=len(self.experience_items) + 1)
                break
        
    def add_experience(self):
        """Add a new experience item."""
        item_frame = customtkinter.CTkFrame(self.sections["experiences"])
        item_frame.grid(row=len(self.experience_items), column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Company
        customtkinter.CTkLabel(item_frame, text="Company:").grid(row=0, column=0, sticky="w", padx=5)
        company_entry = customtkinter.CTkEntry(item_frame)
        company_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Role
        customtkinter.CTkLabel(item_frame, text="Role:").grid(row=1, column=0, sticky="w", padx=5)
        role_entry = customtkinter.CTkEntry(item_frame)
        role_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Dates
        customtkinter.CTkLabel(item_frame, text="Dates:").grid(row=2, column=0, sticky="w", padx=5)
        dates_entry = customtkinter.CTkEntry(item_frame)
        dates_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        # Bullets
        customtkinter.CTkLabel(item_frame, text="Bullets:").grid(row=3, column=0, sticky="w", padx=5)
        bullets_text = customtkinter.CTkTextbox(item_frame, height=100)
        bullets_text.grid(row=3, column=1, sticky="ew", padx=5)
        
        # Delete button
        delete_button = customtkinter.CTkButton(item_frame, text="Delete", command=lambda: self.delete_experience(item_frame))
        delete_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.experience_items.append({
            "frame": item_frame,
            "company": company_entry,
            "role": role_entry,
            "dates": dates_entry,
            "bullets": bullets_text
        })
        
        # Reposition add button
        grid_slaves = self.sections["experiences"].grid_slaves(row=len(self.experience_items) + 1)
        if grid_slaves:
            grid_slaves[0].grid_forget()
        grid_slaves = self.sections["experiences"].grid_slaves(row=len(self.experience_items))
        if grid_slaves:
            grid_slaves[0].grid(row=len(self.experience_items) + 1)
        
    def delete_experience(self, item_frame):
        """Delete an experience item."""
        # Find the item in the list
        for i, item in enumerate(self.experience_items):
            if item["frame"] == item_frame:
                # Remove from the list
                self.experience_items.pop(i)
                # Destroy the frame
                item_frame.destroy()
                # Reposition remaining items
                for j in range(i, len(self.experience_items)):
                    self.experience_items[j]["frame"].grid(row=j)
                # Reposition add button
                grid_slaves = self.sections["experiences"].grid_slaves(row=len(self.experience_items) + 1)
                if grid_slaves:
                    grid_slaves[0].grid_forget()
                grid_slaves = self.sections["experiences"].grid_slaves(row=len(self.experience_items))
                if grid_slaves:
                    grid_slaves[0].grid(row=len(self.experience_items) + 1)
                break
        
    def create_education_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Education items
        education = self.user_data.get("education", [])
        self.education_items = []
        
        for i, edu in enumerate(education):
            item_frame = customtkinter.CTkFrame(frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Degree
            customtkinter.CTkLabel(item_frame, text="Degree:").grid(row=0, column=0, sticky="w", padx=5)
            degree_entry = customtkinter.CTkEntry(item_frame)
            degree_entry.insert(0, edu.get("degree", ""))
            degree_entry.grid(row=0, column=1, sticky="ew", padx=5)
            
            # School
            customtkinter.CTkLabel(item_frame, text="School:").grid(row=1, column=0, sticky="w", padx=5)
            school_entry = customtkinter.CTkEntry(item_frame)
            school_entry.insert(0, edu.get("school", ""))
            school_entry.grid(row=1, column=1, sticky="ew", padx=5)
            
            # Dates
            customtkinter.CTkLabel(item_frame, text="Dates:").grid(row=2, column=0, sticky="w", padx=5)
            dates_entry = customtkinter.CTkEntry(item_frame)
            dates_entry.insert(0, edu.get("dates", ""))
            dates_entry.grid(row=2, column=1, sticky="ew", padx=5)
            
            # Honors
            customtkinter.CTkLabel(item_frame, text="Honors:").grid(row=3, column=0, sticky="w", padx=5)
            honors_text = customtkinter.CTkTextbox(item_frame, height=100)
            honors_text.insert("1.0", "\n".join(edu.get("honors", [])))
            honors_text.grid(row=3, column=1, sticky="ew", padx=5)
            
            self.education_items.append({
                "degree": degree_entry,
                "school": school_entry,
                "dates": dates_entry,
                "honors": honors_text
            })
            
        # Add new education button
        add_button = customtkinter.CTkButton(
            frame,
            text="Add Education",
            command=self.add_education
        )
        add_button.grid(row=len(education), column=0, sticky="ew", padx=5, pady=5)
        
        return frame
        
    def create_certifications_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Certification items
        certifications = self.user_data.get("certifications", [])
        self.certification_items = []
        
        for i, cert in enumerate(certifications):
            item_frame = customtkinter.CTkFrame(frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Name
            customtkinter.CTkLabel(item_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5)
            name_entry = customtkinter.CTkEntry(item_frame)
            name_entry.insert(0, cert.get("name", ""))
            name_entry.grid(row=0, column=1, sticky="ew", padx=5)
            
            # Organization
            customtkinter.CTkLabel(item_frame, text="Organization:").grid(row=1, column=0, sticky="w", padx=5)
            org_entry = customtkinter.CTkEntry(item_frame)
            org_entry.insert(0, cert.get("organization", ""))
            org_entry.grid(row=1, column=1, sticky="ew", padx=5)
            
            # Year
            customtkinter.CTkLabel(item_frame, text="Year:").grid(row=2, column=0, sticky="w", padx=5)
            year_entry = customtkinter.CTkEntry(item_frame)
            year_entry.insert(0, cert.get("year", ""))
            year_entry.grid(row=2, column=1, sticky="ew", padx=5)
            
            self.certification_items.append({
                "name": name_entry,
                "organization": org_entry,
                "year": year_entry
            })
            
        # Add new certification button
        add_button = customtkinter.CTkButton(
            frame,
            text="Add Certification",
            command=self.add_certification
        )
        add_button.grid(row=len(certifications), column=0, sticky="ew", padx=5, pady=5)
        
        return frame
        
    def create_languages_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Language items
        languages = self.user_data.get("languages", [])
        self.language_items = []
        
        for i, lang in enumerate(languages):
            item_frame = customtkinter.CTkFrame(frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Language
            customtkinter.CTkLabel(item_frame, text="Language:").grid(row=0, column=0, sticky="w", padx=5)
            lang_entry = customtkinter.CTkEntry(item_frame)
            lang_entry.insert(0, lang.get("language", ""))
            lang_entry.grid(row=0, column=1, sticky="ew", padx=5)
            
            # Proficiency
            customtkinter.CTkLabel(item_frame, text="Proficiency:").grid(row=1, column=0, sticky="w", padx=5)
            prof_entry = customtkinter.CTkEntry(item_frame)
            prof_entry.insert(0, lang.get("proficiency", ""))
            prof_entry.grid(row=1, column=1, sticky="ew", padx=5)
            
            self.language_items.append({
                "language": lang_entry,
                "proficiency": prof_entry
            })
            
        # Add new language button
        add_button = customtkinter.CTkButton(
            frame,
            text="Add Language",
            command=self.add_language
        )
        add_button.grid(row=len(languages), column=0, sticky="ew", padx=5, pady=5)
        
        return frame
        
    def create_special_instructions_section(self, parent, key):
        frame = customtkinter.CTkFrame(parent)
        frame.grid_columnconfigure(0, weight=1)
        
        # Instructions list
        instructions_list = customtkinter.CTkTextbox(frame, height=100)
        instructions_list.insert("1.0", "\n".join(self.user_data.get("special_instructions", [])))
        instructions_list.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        setattr(self, "special_instructions_textbox", instructions_list)
        
        return frame
        
    def add_education(self):
        """Add a new education item."""
        item_frame = customtkinter.CTkFrame(self.sections["education"])
        item_frame.grid(row=len(self.education_items), column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Degree
        customtkinter.CTkLabel(item_frame, text="Degree:").grid(row=0, column=0, sticky="w", padx=5)
        degree_entry = customtkinter.CTkEntry(item_frame)
        degree_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # School
        customtkinter.CTkLabel(item_frame, text="School:").grid(row=1, column=0, sticky="w", padx=5)
        school_entry = customtkinter.CTkEntry(item_frame)
        school_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Dates
        customtkinter.CTkLabel(item_frame, text="Dates:").grid(row=2, column=0, sticky="w", padx=5)
        dates_entry = customtkinter.CTkEntry(item_frame)
        dates_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        # Honors
        customtkinter.CTkLabel(item_frame, text="Honors:").grid(row=3, column=0, sticky="w", padx=5)
        honors_text = customtkinter.CTkTextbox(item_frame, height=100)
        honors_text.grid(row=3, column=1, sticky="ew", padx=5)
        
        # Delete button
        delete_button = customtkinter.CTkButton(item_frame, text="Delete", command=lambda: self.delete_education(item_frame))
        delete_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.education_items.append({
            "frame": item_frame,
            "degree": degree_entry,
            "school": school_entry,
            "dates": dates_entry,
            "honors": honors_text
        })
        
        # Reposition add button
        grid_slaves = self.sections["education"].grid_slaves(row=len(self.education_items) + 1)
        if grid_slaves:
            grid_slaves[0].grid_forget()
        grid_slaves = self.sections["education"].grid_slaves(row=len(self.education_items))
        if grid_slaves:
            grid_slaves[0].grid(row=len(self.education_items) + 1)
        
    def delete_education(self, item_frame):
        """Delete an education item."""
        # Find the item in the list
        for i, item in enumerate(self.education_items):
            if item["frame"] == item_frame:
                # Remove from the list
                self.education_items.pop(i)
                # Destroy the frame
                item_frame.destroy()
                # Reposition remaining items
                for j in range(i, len(self.education_items)):
                    self.education_items[j]["frame"].grid(row=j)
                # Reposition add button
                grid_slaves = self.sections["education"].grid_slaves(row=len(self.education_items) + 1)
                if grid_slaves:
                    grid_slaves[0].grid_forget()
                grid_slaves = self.sections["education"].grid_slaves(row=len(self.education_items))
                if grid_slaves:
                    grid_slaves[0].grid(row=len(self.education_items) + 1)
                break
        
    def add_certification(self):
        """Add a new certification item."""
        item_frame = customtkinter.CTkFrame(self.sections["certifications"])
        item_frame.grid(row=len(self.certification_items), column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Name
        customtkinter.CTkLabel(item_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5)
        name_entry = customtkinter.CTkEntry(item_frame)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Organization
        customtkinter.CTkLabel(item_frame, text="Organization:").grid(row=1, column=0, sticky="w", padx=5)
        org_entry = customtkinter.CTkEntry(item_frame)
        org_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Year
        customtkinter.CTkLabel(item_frame, text="Year:").grid(row=2, column=0, sticky="w", padx=5)
        year_entry = customtkinter.CTkEntry(item_frame)
        year_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        # Delete button
        delete_button = customtkinter.CTkButton(item_frame, text="Delete", command=lambda: self.delete_certification(item_frame))
        delete_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.certification_items.append({
            "frame": item_frame,
            "name": name_entry,
            "organization": org_entry,
            "year": year_entry
        })
        
        # Reposition add button
        grid_slaves = self.sections["certifications"].grid_slaves(row=len(self.certification_items) + 1)
        if grid_slaves:
            grid_slaves[0].grid_forget()
        grid_slaves = self.sections["certifications"].grid_slaves(row=len(self.certification_items))
        if grid_slaves:
            grid_slaves[0].grid(row=len(self.certification_items) + 1)
        
    def delete_certification(self, item_frame):
        """Delete a certification item."""
        # Find the item in the list
        for i, item in enumerate(self.certification_items):
            if item["frame"] == item_frame:
                # Remove from the list
                self.certification_items.pop(i)
                # Destroy the frame
                item_frame.destroy()
                # Reposition remaining items
                for j in range(i, len(self.certification_items)):
                    self.certification_items[j]["frame"].grid(row=j)
                # Reposition add button
                grid_slaves = self.sections["certifications"].grid_slaves(row=len(self.certification_items) + 1)
                if grid_slaves:
                    grid_slaves[0].grid_forget()
                grid_slaves = self.sections["certifications"].grid_slaves(row=len(self.certification_items))
                if grid_slaves:
                    grid_slaves[0].grid(row=len(self.certification_items) + 1)
                break
        
    def add_language(self):
        """Add a new language item."""
        item_frame = customtkinter.CTkFrame(self.sections["languages"])
        item_frame.grid(row=len(self.language_items), column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Language
        customtkinter.CTkLabel(item_frame, text="Language:").grid(row=0, column=0, sticky="w", padx=5)
        lang_entry = customtkinter.CTkEntry(item_frame)
        lang_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Proficiency
        customtkinter.CTkLabel(item_frame, text="Proficiency:").grid(row=1, column=0, sticky="w", padx=5)
        prof_entry = customtkinter.CTkEntry(item_frame)
        prof_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Delete button
        delete_button = customtkinter.CTkButton(item_frame, text="Delete", command=lambda: self.delete_language(item_frame))
        delete_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.language_items.append({
            "frame": item_frame,
            "language": lang_entry,
            "proficiency": prof_entry
        })
        
        # Reposition add button
        grid_slaves = self.sections["languages"].grid_slaves(row=len(self.language_items) + 1)
        if grid_slaves:
            grid_slaves[0].grid_forget()
        grid_slaves = self.sections["languages"].grid_slaves(row=len(self.language_items))
        if grid_slaves:
            grid_slaves[0].grid(row=len(self.language_items) + 1)
        
    def delete_language(self, item_frame):
        """Delete a language item."""
        # Find the item in the list
        for i, item in enumerate(self.language_items):
            if item["frame"] == item_frame:
                # Remove from the list
                self.language_items.pop(i)
                # Destroy the frame
                item_frame.destroy()
                # Reposition remaining items
                for j in range(i, len(self.language_items)):
                    self.language_items[j]["frame"].grid(row=j)
                # Reposition add button
                grid_slaves = self.sections["languages"].grid_slaves(row=len(self.language_items) + 1)
                if grid_slaves:
                    grid_slaves[0].grid_forget()
                grid_slaves = self.sections["languages"].grid_slaves(row=len(self.language_items))
                if grid_slaves:
                    grid_slaves[0].grid(row=len(self.language_items) + 1)
                break
        
    def add_new_section(self):
        """Add a new custom section to the profile."""
        dialog = customtkinter.CTkInputDialog(
            text="Enter section name:",
            title="Add New Section"
        )
        section_name = dialog.get_input()
        
        if section_name:
            key = section_name.lower().replace(" ", "_")
            frame = customtkinter.CTkFrame(self.scrollable_frame)
            frame.grid(row=len(self.sections), column=0, padx=20, pady=10, sticky="ew")
            frame.grid_columnconfigure(0, weight=1)
            
            label = customtkinter.CTkLabel(frame, text=section_name, font=("Arial", 14, "bold"))
            label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            content = self.create_custom_section(frame, key)
            content.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            
            self.sections[key] = content
            
            # Update button positions
            self.add_section_button.grid(row=len(self.sections), column=0, padx=20, pady=20, sticky="ew")
            self.save_button.grid(row=len(self.sections) + 1, column=0, padx=20, pady=20, sticky="ew")
            
    def save_profile(self):
        """Save the profile data to user.json."""
        try:
            # Update user data
            self.user_data["personal_info"] = {
                key: getattr(self, f"personal_info_{key}").get()
                for key in ["name", "address", "phone", "email", "linkedin", "website", "github"]
            }
            
            self.user_data["eligibility"] = {
                key: getattr(self, f"eligibility_{key}").get()
                for key in ["work_eligibility", "visa_sponsorship_needed", "security_clearance", "willing_to_relocate", "willing_to_travel"]
            }
            
            self.user_data["demographics"] = {
                key: getattr(self, f"demographics_{key}").get()
                for key in ["gender", "race_ethnicity", "veteran_status", "disability_status", "preferred_pronouns"]
            }
            
            self.user_data["skills"] = self.skills_textbox.get("1.0", "end-1c").split("\n")
            
            # Update experiences
            self.user_data["experiences"] = []
            for item in self.experience_items:
                self.user_data["experiences"].append({
                    "company": item["company"].get(),
                    "role": item["role"].get(),
                    "dates": item["dates"].get(),
                    "bullets": item["bullets"].get("1.0", "end-1c").split("\n")
                })
                
            # Update education
            self.user_data["education"] = []
            for item in self.education_items:
                self.user_data["education"].append({
                    "degree": item["degree"].get(),
                    "school": item["school"].get(),
                    "dates": item["dates"].get(),
                    "honors": item["honors"].get("1.0", "end-1c").split("\n")
                })
                
            # Update certifications
            self.user_data["certifications"] = []
            for item in self.certification_items:
                self.user_data["certifications"].append({
                    "name": item["name"].get(),
                    "organization": item["organization"].get(),
                    "year": item["year"].get()
                })
                
            # Update languages
            self.user_data["languages"] = []
            for item in self.language_items:
                self.user_data["languages"].append({
                    "language": item["language"].get(),
                    "proficiency": item["proficiency"].get()
                })
                
            self.user_data["special_instructions"] = self.special_instructions_textbox.get("1.0", "end-1c").split("\n")
            
            # Update custom sections
            for section_name, section in self.sections.items():
                if section_name not in self.user_data:
                    items = getattr(self, f"{section_name}_items", [])
                    self.user_data[section_name] = [
                        item["content"].get("1.0", "end-1c")
                        for item in items
                    ]
            
            # Write to file
            user_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config", "user.json")
            with open(user_file, 'w') as f:
                json.dump(self.user_data, f, indent=4)
                
            messagebox.showinfo("Success", "Profile saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")

    def delete_section(self, key, section_frame):
        """Delete a section from the profile."""
        # Remove the section from user_data
        if key in self.user_data:
            del self.user_data[key]
        
        # Destroy the section frame
        section_frame.destroy()
        
        # Remove the section from the sections dictionary
        if key in self.sections:
            del self.sections[key]
        
        # Reposition remaining sections
        for i, (k, frame) in enumerate(self.sections.items()):
            frame.grid(row=i) 