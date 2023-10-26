from typing import List

import gtts
import os
import PyPDF2
import tkinter
from tkinter import filedialog
import sys
import re

import tkinter as tk
import tkinter.filedialog as fd


class Window:
    pdf_file_path = ""
    directory_path = ""
    chapters = []
    all_chapters = []
    texts = []

    def __init__(self, master):
        self.master = master
        self.master.title("PDF to Speech Converter")

        # Create a label for the PDF file input field.
        self.pdf_file_label = tk.Label(self.master, text="PDF file:")
        self.pdf_file_label.grid(row=0, column=0, sticky="W")

        # Create a PDF file input field.
        self.pdf_file_entry = tk.Entry(self.master)
        self.pdf_file_entry.grid(row=0, column=1, sticky="WE")

        # Create a browse button for the PDF file input field.
        self.pdf_file_browse_button = tk.Button(self.master, text="Browse...", command=self.browse_for_pdf_file)
        self.pdf_file_browse_button.grid(row=0, column=2, sticky="E")

        # Create a label for the directory input field.
        self.directory_label = tk.Label(self.master, text="Destination folder:")
        self.directory_label.grid(row=1, column=0, sticky="W")

        # Create a directory input field.
        self.directory_entry = tk.Entry(self.master)
        self.directory_entry.grid(row=1, column=1, sticky="WE")

        # Create a browse button for the directory input field.
        self.directory_browse_button = tk.Button(self.master, text="Browse...", command=self.browse_for_directory)
        self.directory_browse_button.grid(row=1, column=2, sticky="E")

        # Set the focus to the PDF file input field.
        self.pdf_file_entry.focus_set()

        # Create a button to start audio file generation
        self.start_button = tk.Button(self.master, text="Start", command=self.process)
        self.start_button.grid(row=3, column=1, sticky="E")

    def process(self):
        self.chapters = self.find_chapters()
        self.all_chapters = self.create_list_of_all_chapters(self.chapters)
        self.texts = self.create_text_parts(self.all_chapters)
        titles = []
        for chapter in self.chapters:
            if (len(chapter[1]) > 1):
                titles.append([chapter[0] + " - " + elem for elem in chapter[1]])
            else:
                titles.append([chapter[0]])
        titles_list = []
        for sublist in titles:
            for element in sublist:
                titles_list.append(element)
        i = 0
        self.texts = [text for text in self.texts if len(text.strip().split("\n")) > 1]
        for text in self.texts:
            audio_ro, audio_en = self.text_to_speech(text)
            self.create_files(audio_ro, audio_en, titles_list[i])
            i += 1
        self.raise_information_window()
        self.master.after(5000, sys.exit(0))

    def browse_for_pdf_file(self):
        # Get the path to the selected PDF file.
        self.pdf_file_path = fd.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        # If a PDF file was selected, set the path to the PDF file input field.
        if self.pdf_file_path is not None:
            self.pdf_file_entry.delete(0, "end")
            self.pdf_file_entry.insert(0, self.pdf_file_path)

    def browse_for_directory(self):
        # Get the path to the selected directory.
        self.directory_path = fd.askdirectory()

        # If a directory was selected, set the path to the directory input field.
        if self.directory_path is not None:
            self.directory_entry.delete(0, "end")
            self.directory_entry.insert(0, self.directory_path)

    def raise_information_window(self):
        # Create an information window.
        information_window = tk.Toplevel()
        information_window.title("Information")

        # Add a label to the information window.
        information_label = tk.Label(information_window, text="The function has completed successfully.")
        information_label.pack()

        # Raise the information window.
        information_window.lift()

    def find_chapters(self):
        # Create a PyPDF2 object
        self.pdf = PyPDF2.PdfReader(self.pdf_file_path)
        # Extract the chapters from the PDF file
        chapters = []
        # create a chapter structure where we can find all the main chapters from the table of contents and the subchapters that belong ot it
        for page in self.pdf.pages:
            if page.extract_text().lower().startswith("contents") or page.extract_text().lower().startswith("cuprins"):
                text = page.extract_text()
                lines = list(text.split("\n"))
                lines = [l.strip() for l in lines]
                lines = [l for l in lines if l != ""]
                print(lines)
                i = 0
                while i in range(len(lines)):
                    line = lines[i]
                    if "chapter " in line.lower() or "capitol " in line.lower():
                        pattern = r"([A-Za-z][A-Za-z0-9: ]+)"
                        matches = re.findall(pattern, line)
                        matches = [match.strip() for match in matches]
                        chapter_with_subchapters = [matches[0], []]
                        if i + 1 >= len(lines): break
                        i += 1
                        line = lines[i]
                        while i in range(len(lines)) and not (
                                "chapter " in line.lower() or "capitolul " in line.lower()):
                            pattern = r"([A-Za-z][A-Za-z0-9 ]+)"
                            matches = re.findall(pattern, line)
                            matches = [match.strip() for match in matches]
                            chapter_with_subchapters[1].append(matches[0])
                            if i + 1 >= len(lines): break
                            i += 1
                            line = lines[i]
                        chapters.append(chapter_with_subchapters)
                    elif "introduction" in line.lower() or "introducere" in line.lower():
                        pattern = r"([A-Za-z][A-Za-z0-9: ]+)"
                        matches = re.findall(pattern, line)
                        matches = [match.strip() for match in matches]
                        chapter_with_subchapters = [matches[0], []]
                        chapters.append(chapter_with_subchapters)
                        i += 1
                    elif "conclusions" in line.lower() or "concluzii" in line.lower():
                        pattern = r"([A-Za-z][A-Za-z0-9: ]+)"
                        matches = re.findall(pattern, line)
                        matches = [match.strip() for match in matches]
                        chapter_with_subchapters = [matches[0], []]
                        chapters.append(chapter_with_subchapters)
                        i += 1
                    else:
                        i += 1
        return chapters

    def create_list_of_all_chapters(self, chapters):
        # create a list of all the chapters and subchapters
        print(chapters)
        chapters0 = [[chapter[0]] + chapter[1] for chapter in chapters]
        chapter_list = []
        for sublist in chapters0:
            for element in sublist:
                chapter_list.append(element)
        return chapter_list

    def split_string_at_nth_appearance_of_delimiter(self, string, delimiter, n=2):
        split_string = string.split(delimiter)
        return [split_string[:n], split_string[n:]]

    def create_text_parts(self, chapters):
        all_chapters = chapters
        texts = []
        txt = ""  # creating one string from all the book
        for page in self.pdf.pages:
            txt += page.extract_text()

        # iterating over all the chapters
        while len(all_chapters) > 0:
            split_string = self.split_string_at_nth_appearance_of_delimiter(txt, all_chapters[0])
            chapter = all_chapters[0] + "\n\n"
            if len(all_chapters) > 1:
                for string in split_string[1]:
                    if all_chapters[1] in string:
                        # a=string.split(all_chapters[1])
                        chapter += string.split(all_chapters[1])[0]
                    else:
                        chapter += string
            else:
                for string in split_string[1]:
                    chapter += string
            all_chapters = all_chapters[1:]
            texts.append(chapter)

        # i = 0
        # while i in range(len(self.pdf.pages)):
        #     header = self.pdf.pages[i].extract_text().lower()
        #     if all_chapters[0] in header and not header.startswith("contents") and not header.startswith("cuprins"):  # if we found the chapter or subchapter title in the current page
        #         text_parts = header.split(all_chapters[0])
        #         text_parts = [t.split() for t in text_parts if t != ""]
        #         text = ""
        #         if len(text_parts) == 2:  # we found a subchapter that is in the middle of the page and splits the page in half
        #             text += text_parts[1]
        #         else:
        #             text += self.pdf.pages[i].extract_text()
        #         if i + 1 >= len(self.pdf.pages): break
        #         i += 1
        #         page = self.pdf.pages[i]
        #         # no similarities with the next chapter title
        #         while i in range(len(self.pdf.pages)) and not all_chapters[1] in page.extract_text().lower():
        #             text += page.extract_text()
        #             if i + 1 >= len(self.pdf.pages): break
        #             i += 1
        #             page = self.pdf.pages[i]
        #         if i in range(len(self.pdf.pages)) and all_chapters[1] in page.extract_text().lower():
        #             text_parts = header.split(all_chapters[1])
        #             text+=text_parts[0] # the first half is the ending of the current subchapter
        #         texts.append(text)
        #         all_chapters = all_chapters[1:]
        #     i += 1
        return texts

    def create_files(self, audio_ro, audio_en, title):
        # create output directories
        path_en = os.path.join(self.directory_path, "Chapters")
        try:
            os.mkdir(path_en)
        except:
            pass
        path_ro = os.path.join(self.directory_path, "Capitole")
        try:
            os.mkdir(path_ro)
        except:
            pass
        title = title.replace(":", "")
        name_ro = path_ro + "\\" + title + ".mp3"
        name_ro = name_ro.replace(" ", "_")
        name_ro = name_ro.replace("/", "\\")
        name_en = path_en + "\\" + title + ".mp3"
        name_en = name_en.replace(" ", "_")
        name_en = name_en.replace("/", "\\")
        audio_ro.save(name_ro)
        audio_en.save(name_en)

    def text_to_speech(self, text):
        # Create a gTTS object for English
        audio_en = gtts.gTTS(text=text, lang="en", slow=False, lang_check=True,
                             pre_processor_funcs=[gtts.tokenizer.pre_processors.tone_marks,
                                                  gtts.tokenizer.pre_processors.abbreviations])
        # Create a gTTS object for Romanian
        audio_ro = gtts.gTTS(text=text, lang="ro", slow=False, lang_check=True,
                             pre_processor_funcs=[gtts.tokenizer.pre_processors.tone_marks,
                                                  gtts.tokenizer.pre_processors.abbreviations])
        return audio_ro, audio_en


if __name__ == "__main__":
    root = tk.Tk()
    window = Window(root)
    root.mainloop()
