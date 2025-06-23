import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from base_tab import BaseTab
from utils import LargeEntryDialog

class CertificationsTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Certifications", "certifications.json")
        self.certifications = []
        self.last_selected_index = None
        self.build_ui()

    def build_ui(self):
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Certifications").pack()
        self.cert_listbox = tk.Listbox(left_frame, width=40, exportselection=False)
        self.cert_listbox.pack(fill=tk.Y, expand=True)
        self.cert_listbox.bind("<<ListboxSelect>>", self.on_cert_select)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_certification).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Delete", command=self.delete_certification).pack(side=tk.LEFT)

        right_frame = tk.Frame(self.frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(right_frame, width=50)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(right_frame, text="Link:").grid(row=1, column=0, sticky="w")
        self.link_entry = tk.Entry(right_frame, width=50)
        self.link_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(right_frame, text="Date:").grid(row=2, column=0, sticky="w")
        self.date_entry = tk.Entry(right_frame, width=50)
        self.date_entry.grid(row=2, column=1, sticky="ew", pady=2)

        right_frame.columnconfigure(1, weight=1)

        tk.Button(right_frame, text="Save Changes", command=self.save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    def add_certification(self):
        dlg = LargeEntryDialog(self.frame, title="Add Certification", prompt="Enter certification name:")
        new_name = dlg.result
        if not new_name:
            return
        new_name = new_name.strip()
        if any(cert["name"] == new_name for cert in self.certifications):
            messagebox.showerror("Error", "Certification already exists.")
            return
        self.certifications.append({"name": new_name, "link": "", "date": ""})
        self.refresh_list()
        self.cert_listbox.selection_clear(0, tk.END)
        self.cert_listbox.selection_set(tk.END)
        self.on_cert_select()
        self.autosave()

    def delete_certification(self):
        sel = self.cert_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a certification to delete.")
            return
        idx = sel[0]
        cert = self.certifications[idx]
        if messagebox.askyesno("Confirm", f"Delete certification '{cert['name']}'?"):
            del self.certifications[idx]
            self.refresh_list()
            self.clear_fields()
            self.autosave()

    def on_cert_select(self, event=None):
        sel = self.cert_listbox.curselection()
        if not sel:
            self.clear_fields()
            self.last_selected_index = None
            return
        idx = sel[0]
        cert = self.certifications[idx]
        self.last_selected_index = idx

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, cert["name"])

        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, cert["link"])

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, cert["date"])

    def save_changes(self):
        if self.last_selected_index is None:
            messagebox.showinfo("Info", "Select a certification first.")
            return

        name = self.name_entry.get().strip()
        link = self.link_entry.get().strip()
        date = self.date_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Certification name cannot be empty.")
            return

        for i, cert in enumerate(self.certifications):
            if i != self.last_selected_index and cert["name"] == name:
                messagebox.showerror("Error", "Another certification with this name already exists.")
                return

        cert = self.certifications[self.last_selected_index]
        cert["name"] = name
        cert["link"] = link
        cert["date"] = date

        self.refresh_list()
        self.cert_listbox.selection_clear(0, tk.END)
        self.cert_listbox.selection_set(self.last_selected_index)
        self.autosave()

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.link_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def refresh_list(self):
        self.cert_listbox.delete(0, tk.END)
        for cert in self.certifications:
            self.cert_listbox.insert(tk.END, cert["name"])

    def get_data(self):
        return self.certifications

    def load_data(self, data):
        self.certifications = []
        if not isinstance(data, list):
            return
        for item in data:
            if isinstance(item, dict) and "name" in item:
                self.certifications.append({
                    "name": item["name"],
                    "link": item.get("link", ""),
                    "date": item.get("date", "")
                })
        self.refresh_list()
        self.clear_fields()
        self.last_selected_index = None
