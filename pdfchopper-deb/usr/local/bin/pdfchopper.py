# App uses tkinterdnd2 for drag-and-drop functionality.
# pip install tkinterdnd2

# App uses tkinter for GUI.
# sudo apt-get install python3-tk

# App uses qpdf for PDF manipulation.
# Install qpdf on Debian/Ubuntu with:
# sudo apt install qpdf

import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
import re

MAX_ENTRIES=15
HOME = os.path.expanduser("~")
PDFCHOPPER_CONFIG_FOLDER = os.path.join(HOME, ".pdfchopper")
PDFCHOPPER_CONFIG_LIBRARY_FOLDER = os.path.join(PDFCHOPPER_CONFIG_FOLDER, "library")
if not os.path.exists(PDFCHOPPER_CONFIG_LIBRARY_FOLDER):
    os.makedirs(PDFCHOPPER_CONFIG_LIBRARY_FOLDER)


class PDFChopper(TkinterDnD.Tk):
    default_export_folder = ""
    parent_export_folder = ""
    loaded_file_path = ""
    default_config_file_path = ""
    use_library = True


    def __init__(self):
        super().__init__()
        self.title("PDF Chopper")
        self.load_program_settings()  # Load window position if available

        # Drag and Drop setup - all frame will support file drops
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop_file)

        top_frame = tk.Frame(self)
        top_frame.pack(pady=5)

        top_frame.drag_drop_label=tk.Label(top_frame, text="Drop PDF file to chop", bg="lightgray", width=30, height=2)
        top_frame.drag_drop_label.pack()

        self.file_label = tk.Label(top_frame, text="No file selected")
        self.file_label.pack()

        # PDF File Load
        file_frame = tk.Frame(self)
        file_frame.pack(pady=20)

        # self.load_pdf_button = tk.Button(file_frame, text="Load PDF File", command=self.load_pdf)
        # self.load_pdf_button.pack(side="left", padx=10)

        self.save_default_folder_button = tk.Button(file_frame, text="Save As Default", command=self.save_as_default_export_folder)
        self.save_default_folder_button.pack(side="left", padx=10)
        if not self.default_export_folder:
            self.save_default_folder_button.config(state="disabled")

        self.default_folder_button = tk.Button(file_frame, text="Default", command=self.select_default_export_folder)
        self.default_folder_button.pack(side="left", padx=10)
        if not self.default_export_folder:
            self.default_folder_button.config(state="disabled")

        self.parent_folder_button = tk.Button(file_frame, text="Parent", command=self.select_parent_export_folder)
        self.parent_folder_button.pack(side="left", padx=10)
        if not self.parent_export_folder:
            self.parent_folder_button.config(state="disabled")

        self.export_folder_button = tk.Button(file_frame, text="Export Folder", command=self.select_export_folder)
        self.export_folder_button.pack(side="left", padx=10)

        self.export_folder_label = tk.Label(file_frame, text=self.default_export_folder)
        self.export_folder_label.pack(side="left")

        self.export_folder_label.drop_target_register(DND_FILES)
        self.export_folder_label.dnd_bind('<<Drop>>', self.on_drop_folder)

        # Input fields
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)

        # Arrange "Repeat at start" and "Repeat at end" on the same row
        tk.Label(self.input_frame, text="Repeat at start:").grid(row=1, column=0, padx=5, sticky="e")
        self.repeat_start = tk.Entry(self.input_frame, width=10,state="disabled")
        self.repeat_start.grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(self.input_frame, text="Repeat at end:").grid(row=1, column=2, padx=5, sticky="e")
        self.repeat_end = tk.Entry(self.input_frame, width=10,state="disabled")
        self.repeat_end.grid(row=1, column=3, padx=5, sticky="w")

        tk.Label(self.input_frame, text="Output base name:").grid(row=1, column=4, padx=5, sticky="e")
        self.output_base_name = tk.Entry(self.input_frame, width=20,state="disabled")
        self.output_base_name.grid(row=1, column=5, padx=5, sticky="w")

        self.rows_frame = tk.Frame(self)
        self.rows_frame.pack(padx=10,pady=10)

        self.row_data = []

        # tk.Label(self.rows_frame, text="Use").grid(row=0, column=0, padx=5, sticky="w")
        tk.Label(self.rows_frame, text="Pages").grid(row=0, column=1, padx=5, sticky="w")
        tk.Label(self.rows_frame, text="Optional description (just for your reference)").grid(row=0, column=3, padx=5, sticky="w")
        tk.Label(self.rows_frame, text="Base + Output name").grid(row=0, column=4, padx=5, sticky="w")

        self.export_all_button = tk.Button(self.rows_frame, text="Export All", command=self.export_all,state="disabled")
        self.export_all_button.grid(row=0, column=5, padx=5, sticky="w")


        for i in range(1,MAX_ENTRIES+1):
            var = tk.BooleanVar()
            # chk = tk.Checkbutton(self.rows_frame, variable=var)
            # chk.grid(row=i, column=0, padx=5)

            minus_button = tk.Button(self.rows_frame, text="-", command=lambda r=i-1: self.change_all_by(r,-1),state="disabled")
            minus_button.grid(row=i, column=0)

            plus_button = tk.Button(self.rows_frame, text="+", command=lambda r=i-1: self.change_all_by(r,1),state="disabled")
            plus_button.grid(row=i, column=1)

            pages = tk.Entry(self.rows_frame, width=30,state="disabled")
            pages.grid(row=i, column=2, padx=5)

            description_entry = tk.Entry(self.rows_frame, width=40,state="disabled")
            description_entry.grid(row=i, column=3, padx=5)

            outname = tk.Entry(self.rows_frame, width=20,state="disabled")
            outname.grid(row=i, column=4, padx=5)

            save_btn = tk.Button(self.rows_frame, text="Export",state="disabled",command=lambda r=i-1: self.export_one_row(r))
            save_btn.grid(row=i, column=5, padx=5)

            self.row_data.append({
                'checked': var,
                'pages': pages,
                'outname': outname,
                'description': description_entry,
                'save_btn': save_btn,
                'minus_button': minus_button,
                'plus_button': plus_button
            })

        # Buttons for Save / Load / Clear
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.config_label = tk.Label(self.button_frame, text="Configuration:")
        self.config_label.grid(row=0, column=0, padx=5)

        self.use_library_checkbox = tk.Checkbutton(self.button_frame, text="Save in Library", state="disabled")
        self.use_library_checkbox.var = tk.BooleanVar(value=self.use_library)
        self.use_library_checkbox.config(variable=self.use_library_checkbox.var)
        self.use_library_checkbox.grid(row=0, column=1, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_data,state="disabled")
        self.save_button.grid(row=0, column=2, padx=10)

        self.saveas_button = tk.Button(self.button_frame, text="Save As...", command=self.saveas_data,state="disabled")
        self.saveas_button.grid(row=0, column=3, padx=10)

        self.load_button = tk.Button(self.button_frame, text="Load", command=self.load_data,state="disabled")
        self.load_button.grid(row=0, column=4, padx=10)

        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_data,state="disabled")
        self.clear_button.grid(row=0, column=5, padx=10)

        self.just_exit = tk.Button(self.button_frame, text="Exit", command=self.just_close)
        self.just_exit.grid(row=0, column=6, padx=10)

        self.save_exit = tk.Button(self.button_frame, text="Save & Exit", command=self.on_close,state="disabled")
        self.save_exit.grid(row=0, column=7, padx=10)
        
        self.status_frame = tk.Frame(self)
        self.status_frame.pack(fill="x", pady=10)

        self.status_label = tk.Label(self.status_frame, text="Status:", anchor="w")
        self.status_label.pack(side="left", padx=10, fill="x", expand=True)


        # Try loading 'pdfchunker.json' at startup
        # self.after(100, self.try_load_default_file)
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def clear_data(self):
        self.repeat_start.delete(0, tk.END)
        self.repeat_end.delete(0, tk.END)
        self.output_base_name.delete(0, tk.END)

        i=1
        for row in self.row_data:
            row['checked'].set(False)
            row['pages'].delete(0, tk.END)
            row['description'].delete(0, tk.END)
            row['outname'].delete(0, tk.END)
            row['outname'].delete(0, tk.END)
            row['outname'].insert(0, i)
            i=i+1

    def on_drop_folder(self, event):
        folder_path = event.data.strip('{}')  # Remove curly braces if present
        if os.path.isdir(folder_path):
            print(f"Dropped folder: {folder_path}")
            self.export_folder_label.config(text=folder_path)


    def on_drop_file(self, event):
        file_path = event.data.strip('{}')  # Remove curly braces if present
        if file_path.lower().endswith('.pdf'):
            self.clear_data()
            self.loaded_file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.parent_export_folder=os.path.dirname(file_path);
            self.save_default_folder_button.config(state="normal")
            self.parent_folder_button.config(state="normal")
            self.save_button.config(state="normal")
            self.saveas_button.config(state="normal")
            self.load_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.save_exit.config(state="normal")
            self.export_all_button.config(state="normal")
            self.use_library_checkbox.config(state="normal")
            self.repeat_end.config(state="normal")
            self.repeat_start.config(state="normal")
            self.output_base_name.config(state="normal")    

            i=1
            for row in self.row_data:
                row['checked'].set(False)
                row['pages'].config(state="normal")
                row['description'].config(state="normal")
                row['outname'].config(state="normal")
                row['save_btn'].config(state="normal")
                row['outname'].delete(0, tk.END)
                row['outname'].insert(0, i)
                row['minus_button'].config(state="normal")
                row['plus_button'].config(state="normal")
                i=i+1

            self.after(100, self.try_load_default_config_file)
            self.export_folder_label.config(text=self.default_export_folder if self.default_export_folder else self.parent_export_folder)
            self.show_status(f"Loaded PDF: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Invalid file", "Please drop a PDF file.")


    def save_as_default_export_folder(self):
        self.default_export_folder = self.export_folder_label.cget("text")
        

    def select_export_folder(self):
        # Start from PDF's folder if loaded, else home
        current_dir = self.export_folder_label.cget("text")
        folder = filedialog.askdirectory(initialdir=current_dir, title="Select Export Folder")
        if folder:
            self.export_folder_label.config(text=folder)


    def load_data(self):
        initial_dir = os.path.dirname(self.loaded_file_path) if self.loaded_file_path else PDFCHOPPER_CONFIG_LIBRARY_FOLDER
        file_path = filedialog.askopenfilename(initialdir=initial_dir,filetypes=[("JSON Files", "*.json")])
        if file_path:
            self._load_data_from_file(file_path)


    def try_load_default_config_file(self):
        filename = self.file_label.cget("text")
        # Remove _vXX.pdf at the end, where XX can be any length
        base = re.sub(r'_v[^_]+\.pdf$', '', filename, flags=re.IGNORECASE)
        self.default_config_file_path = os.path.join(os.path.dirname(self.loaded_file_path), base + ".json")
        print(f"Searching config file: {self.default_config_file_path}")
        if os.path.exists(self.default_config_file_path):
            self._load_data_from_file(self.default_config_file_path)
        elif os.path.exists(os.path.join(PDFCHOPPER_CONFIG_LIBRARY_FOLDER, base + ".json")):
            self._load_data_from_file(os.path.join(PDFCHOPPER_CONFIG_LIBRARY_FOLDER, base + ".json"))
        else:
            self.show_status(f"No Config Data File was found for {base}.json", fg="red")
            base_name = os.path.splitext(os.path.basename(self.loaded_file_path))[0]
            # Get the part before the first underscore, or the whole name if no underscore
            first_part = base_name.split('_')[0]
            self.output_base_name.insert(0, first_part)


    def _load_data_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")
            return

        # Set values from loaded data
        self.repeat_start.delete(0, tk.END)
        self.repeat_start.insert(0, data.get('repeat_start', ''))

        self.repeat_end.delete(0, tk.END)
        self.repeat_end.insert(0, data.get('repeat_end', ''))

        self.output_base_name.delete(0, tk.END)
        self.output_base_name.insert(0, data.get('output_base', ''))
        if not data.get('output_base', ''):
            # Get the filename without extension
            base_name = os.path.splitext(os.path.basename(self.loaded_file_path))[0]
            # Get the part before the first underscore, or the whole name if no underscore
            first_part = base_name.split('_')[0]
            self.output_base_name.insert(0, first_part)

        rows = data.get('rows', [])
        for i, row_info in enumerate(rows):
            if i < len(self.row_data):
                self.row_data[i]['checked'].set(row_info.get('checked', False))
                self.row_data[i]['pages'].delete(0, tk.END)
                self.row_data[i]['pages'].insert(0, row_info.get('pages', ''))

                self.row_data[i]['outname'].delete(0, tk.END)
                self.row_data[i]['outname'].insert(0, row_info.get('outname', ''))

                self.row_data[i]['description'].delete(0, tk.END)
                self.row_data[i]['description'].insert(0, row_info.get('description', ''))  # Load description

        self.show_status(f"Loaded Config Data: {file_path}")


    def on_close(self):
        if self.loaded_file_path:
            try:
                self.save(True,self.default_config_file_path)  # Save data before closing
                self.save_program_settings();
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        self.destroy()


    def just_close(self):
        self.save_program_settings();
        self.destroy()


    def save_data(self):
        try:
            self.save(False,self.default_config_file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")


    def saveas_data(self):
        try:
            initial_dir = os.path.dirname(self.loaded_file_path) if self.loaded_file_path else PDFCHOPPER_CONFIG_LIBRARY_FOLDER
            save_path = filedialog.asksaveasfilename(initialdir=initial_dir,defaultextension=".json", filetypes=[("JSON Files", "*.json")], initialfile=self.default_config_file_path)
            self.save(False,save_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")


    def save(self,is_closing,save_path):
        data = {
            'last_file': self.loaded_file_path,
            'repeat_start': self.repeat_start.get(),
            'repeat_end': self.repeat_end.get(),
            'output_base': self.output_base_name.get(),
            'rows': []
        }

        for row in self.row_data:
            row_info = {
                'checked': row['checked'].get(),
                'pages': row['pages'].get(),
                'description': row['description'].get(),
                'outname': row['outname'].get()
            }
            data['rows'].append(row_info)

        if self.use_library_checkbox.var.get():
            # Save to library folder
            save_path = os.path.join(PDFCHOPPER_CONFIG_LIBRARY_FOLDER, os.path.basename(save_path))

        if save_path:
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
            if not is_closing:
                self.show_status(f"Config Saved: {save_path}",fg="green")


    def select_parent_export_folder(self):
        self.export_folder_label.config(text=self.parent_export_folder)


    def select_default_export_folder(self):
        self.export_folder_label.config(text=self.default_export_folder)


    def save_program_settings(self):
        data = {"x": self.winfo_x(), "y": self.winfo_y(),
                "export_folder": self.default_export_folder,
                "use_library": self.use_library_checkbox.var.get()}
        home = os.path.expanduser("~")
        path = os.path.join(HOME, PDFCHOPPER_CONFIG_FOLDER, "settings.json")
        with open(path, "w") as f:
            json.dump(data, f)


    def load_program_settings(self):
        path = os.path.join(HOME, PDFCHOPPER_CONFIG_FOLDER, "settings.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    data = json.load(f)
                    x = data.get("x", 100)
                    y = data.get("y", 100)
                    self.default_export_folder=data.get("export_folder", "")
                    self.use_library = data.get("use_library", True)
                    self.geometry(f"+{x}+{y}")
                except Exception:
                    self.geometry("+100+100")
        else:
            self.geometry("+100+100")


    def export_all(self):
        for i,row in enumerate(self.row_data):
            pages_str = self.row_data[i]['pages'].get().strip()
            if pages_str:
                self.export_one_row(i)
            else:
                base_name = self.output_base_name.get().strip()
                outname = self.row_data[i-1]['outname'].get().strip()
                self.show_status(f"Exported all files. Finished with row {i}, {base_name}{outname}.pdf",fg="green")
                return


    def export_one_row(self,row):
        repeat_start = self.repeat_start.get().strip()
        repeat_end = self.repeat_end.get().strip()

        base_name = self.output_base_name.get().strip()
        outname = self.row_data[row]['outname'].get().strip()
        pages_str = self.row_data[row]['pages'].get().strip()

        if not base_name or not outname or not pages_str:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        export_folder = self.export_folder_label.cget("text")
        if not export_folder:
            messagebox.showerror("Error", "Please select an export folder.")
            return

        self.export_pages(base_name, outname+".pdf", repeat_start, pages_str, repeat_end, export_folder)


    def export_pages(self,base_name, outname, repeat_start,pages_str,repeat_end,export_folder):
        pages = PDFChopper.parse_page_ranges(pages_str)
        if not pages:
            messagebox.showerror("Error", "No valid pages specified.")
            return

        result = []
        if repeat_start:
            result.extend(PDFChopper.parse_page_ranges(repeat_start))
        if pages_str:
            result.extend(PDFChopper.parse_page_ranges(pages_str))
        if repeat_end:
            result.extend(PDFChopper.parse_page_ranges(repeat_end))

        # Here you would implement the actual PDF export logic
        # For now, we just print the pages and outname
        print(f"Exporting Pages {result} to {export_folder}/{base_name}{outname}")

        input_file_with_path = self.loaded_file_path
        output_file_with_path = os.path.join(export_folder, f"{base_name}{outname}")
        pages = result
        # print(f"Input file: {input_file_with_path}")
        # print(f"Pages to export: {pages}")
        # print(f"Output file: {output_file_with_path}")  
        PDFChopper.export_with_qpdf(input_file_with_path, pages, output_file_with_path)
        self.show_status(f"Exported Pages {result} to {export_folder}/{base_name}{outname}", fg="green")


    def change_all_by(self,row,value):
        """
        Change all page numbers in the specified row by the given delta.
        If delta is -1, decrement all page numbers by 1.
        If delta is 1, increment all page numbers by 1.
        """
        
        while self.row_data[row]['pages'].get():
            # Get the current pages string, or an empty string if not set
            pages_str = self.row_data[row]['pages'].get().strip()
            if not pages_str:
                return
            # Parse the page ranges
            new_pages_str = PDFChopper.increment_page_ranges(pages_str,value)
            self.row_data[row]['pages'].delete(0, tk.END)
            self.row_data[row]['pages'].insert(0, new_pages_str) 
            row=row+1;


    def show_status(self, message, fg="black"):
        """
        Show a status message in the status label.
        """
        self.status_label.config(text=message, fg=fg)


    @staticmethod
    def export_with_qpdf(input_file_with_path, pages, output_file_with_path):
        """
        Export the specified pages from the input PDF file to the output PDF file using qpdf.
        """
        if not os.path.exists(input_file_with_path):
            raise FileNotFoundError(f"Input file does not exist: {input_file_with_path}")
        if not pages:
            raise ValueError("No pages specified for export.")
        if os.path.exists(output_file_with_path):
            messagebox.showerror("Error", f"Output file {output_file_with_path} already exists. Please choose a different export folder or delete the existing file.")
            raise FileExistsError(f"Output file already exists: {output_file_with_path}")

        # Construct the qpdf command
        pages_str = ','.join(map(str, pages))
        # qpdf input.pdf --pages --file=input.pdf --range=1,2,3 -- output.pdf
        command = f"qpdf {input_file_with_path} --pages --file={input_file_with_path} --range={pages_str} -- {output_file_with_path}"

        # Execute the command
        print(f"Executing: {command}")
        os.system(command)
        

    @staticmethod
    def parse_page_ranges(pages_str):
        """
        Given a string like "1,2,2,3,4-6,5,6", return a list of all page numbers as integers,
        preserving order and repetitions.
        """
        result = []
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start), int(end)
                result.extend(range(start, end + 1))
            elif part:
                result.append(int(part))
        return result


    @staticmethod
    def increment_page_ranges(pages_str,value):
        """
        Given a string like "2,3,4-7,9,10", return a string where each number is incremented by one,
        preserving the original format.
        Example: "2,3,4-7,9,10" -> "3,4,5-8,10,11"
        """
        result = []
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                if start and end:
                    start, end = int(start), int(end)
                    result.append(f"{start+value}-{end+value}")
            elif part:
                result.append(str(int(part)+value))
        return ','.join(result)


if __name__ == "__main__":
    app = PDFChopper()
    app.mainloop()
