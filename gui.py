from pathlib import Path
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.hall import Hall
from src.main import main

BG = "#0f172a"
PANEL = "#1e293b"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#7c3aed"


class SeatingApp:
    def __init__(self, root):
        self.root = root
        root.title("Олимпиада · Рассадка")
        root.geometry("1000x700")
        root.minsize(820, 560)
        root.configure(bg=BG)
        self.file_path = tk.StringVar()
        self.hall_name = tk.StringVar()
        self.hall_capacity = tk.StringVar()
        self.status = tk.StringVar(value="Выберите Excel со списком участников")
        self.result = None
        self.selected_halls = None
        self.configure_styles()
        self.build_layout()
        self.refresh_halls()

    def configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="white",
            padding=(16, 10),
            borderwidth=0,
        )
        style.map("Accent.TButton", background=[("active", "#6d28d9")])
        style.configure(
            "Soft.TButton",
            background="#334155",
            foreground=TEXT,
            padding=(12, 9),
            borderwidth=0,
        )
        style.map("Soft.TButton", background=[("active", "#475569")])
        style.configure(
            "Dark.TEntry",
            fieldbackground=BG,
            foreground=TEXT,
            insertcolor=TEXT,
            padding=8,
        )
        style.configure(
            "Dark.Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Dark.Treeview.Heading", background="#334155", foreground=TEXT, padding=8
        )
        style.map("Dark.Treeview", background=[("selected", ACCENT)])

    def label(self, parent, text, size=11, color=TEXT, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent["bg"],
            fg=color,
            font=("DejaVu Sans", size, "bold" if bold else "normal"),
            anchor="w",
        )

    def card(self, parent):
        return tk.Frame(parent, bg=PANEL, padx=20, pady=18)

    def build_layout(self):
        page = tk.Frame(self.root, bg=BG, padx=28, pady=24)
        page.pack(fill="both", expand=True)
        self.label(page, "Рассадка участников", 23, bold=True).pack(fill="x")
        self.label(
            page, "Загрузите список, проверьте залы и сохраните результат.", color=MUTED
        ).pack(fill="x", pady=(4, 20))

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x")
        top.grid_columnconfigure(0, weight=3)
        top.grid_columnconfigure(1, weight=2)

        source = self.card(top)
        source.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.label(source, "01   Список участников", 14, bold=True).pack(fill="x")
        self.label(source, "Файл Excel (.xlsx)", color=MUTED).pack(
            fill="x", pady=(18, 6)
        )
        file_row = tk.Frame(source, bg=PANEL)
        file_row.pack(fill="x")
        ttk.Entry(file_row, textvariable=self.file_path, style="Dark.TEntry").pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        ttk.Button(
            file_row, text="Обзор…", style="Soft.TButton", command=self.choose_file
        ).pack(side="right")
        self.label(
            source, "Соседство проверяется по школе и возрастной группе.", 10, MUTED
        ).pack(fill="x", pady=(18, 0))

        rooms = self.card(top)
        rooms.grid(row=0, column=1, sticky="nsew")
        self.label(rooms, "02   Залы", 14, bold=True).pack(fill="x")
        self.hall_tree = ttk.Treeview(
            rooms,
            columns=("enabled", "name", "capacity"),
            show="headings",
            height=4,
            style="Dark.Treeview",
        )
        self.hall_tree.heading("enabled", text="✓")
        self.hall_tree.heading("name", text="Название")
        self.hall_tree.heading("capacity", text="Мест")
        self.hall_tree.column(
            "enabled", width=36, minwidth=36, stretch=False, anchor="center"
        )
        self.hall_tree.column("name", width=170)
        self.hall_tree.column("capacity", width=60, anchor="center")
        self.hall_tree.bind("<ButtonRelease-1>", self.toggle_hall)
        self.hall_tree.pack(fill="x", pady=(12, 8))
        self.label(
            rooms, "Нажмите на галочку, чтобы включить зал в рассадку.", 10, MUTED
        ).pack(fill="x", pady=(0, 8))
        self.label(rooms, "Новый зал: название и число мест", 10, MUTED).pack(
            fill="x", pady=(0, 5)
        )
        form = tk.Frame(rooms, bg=PANEL)
        form.pack(fill="x")
        ttk.Entry(
            form, textvariable=self.hall_name, style="Dark.TEntry", width=16
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Entry(
            form, textvariable=self.hall_capacity, style="Dark.TEntry", width=6
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            form, text="Добавить", style="Soft.TButton", command=self.add_hall
        ).pack(side="left")
        ttk.Button(
            rooms,
            text="Удалить зал навсегда",
            style="Soft.TButton",
            command=self.delete_hall,
        ).pack(anchor="w", pady=(8, 0))

        actions = tk.Frame(page, bg=BG)
        actions.pack(fill="x", pady=16)
        ttk.Button(
            actions,
            text="Рассадить участников",
            style="Accent.TButton",
            command=self.run_seating,
        ).pack(side="left")
        self.save_button = ttk.Button(
            actions,
            text="Сохранить Excel…",
            style="Soft.TButton",
            command=self.save_result,
            state="disabled",
        )
        self.save_button.pack(side="left", padx=(10, 0))

        results = self.card(page)
        results.pack(fill="both", expand=True)
        self.label(results, "03   Результат", 14, bold=True).pack(
            fill="x", pady=(0, 10)
        )
        table = tk.Frame(results, bg=PANEL)
        table.pack(fill="both", expand=True)
        columns = ("name", "school", "grade", "hall", "seat")
        self.result_tree = ttk.Treeview(
            table, columns=columns, show="headings", style="Dark.Treeview"
        )
        self.result_tree.tag_configure("unseated", foreground="#fca5a5")
        for key, title, width in (
            ("name", "Участник", 210),
            ("school", "Название школы", 170),
            ("grade", "Класс", 70),
            ("hall", "Зал", 145),
            ("seat", "Место", 70),
        ):
            self.result_tree.heading(key, text=title)
            self.result_tree.column(
                key, width=width, anchor="center" if key in ("grade", "seat") else "w"
            )
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scroll.set)
        self.result_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.status_label = self.label(page, "", 10, MUTED)
        self.status_label.configure(textvariable=self.status)
        self.status_label.pack(fill="x", pady=(12, 0))

    def refresh_halls(self):
        try:
            halls = Hall.load_halls()
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror(
                "Не удалось загрузить залы", str(exc), parent=self.root
            )
            return
        names = {hall.name for hall in halls}
        if self.selected_halls is None:
            self.selected_halls = names.copy()
        else:
            self.selected_halls.intersection_update(names)
        self.hall_tree.delete(*self.hall_tree.get_children())
        for hall in halls:
            mark = "☑" if hall.name in self.selected_halls else "☐"
            self.hall_tree.insert(
                "", "end", values=(mark, hall.name, hall.workspace_quantity)
            )

    def toggle_hall(self, event):
        if self.hall_tree.identify_column(event.x) != "#1":
            return
        item = self.hall_tree.identify_row(event.y)
        if not item:
            return
        name = self.hall_tree.item(item, "values")[1]
        if name in self.selected_halls:
            self.selected_halls.remove(name)
            mark = "☐"
        else:
            self.selected_halls.add(name)
            mark = "☑"
        self.hall_tree.set(item, "enabled", mark)
        self.clear_result()
        self.status.set(f"Для рассадки выбрано залов: {len(self.selected_halls)}")

    def choose_file(self):
        if shutil.which("zenity"):
            dialog = subprocess.run(
                [
                    "zenity",
                    "--file-selection",
                    "--modal",
                    "--title=Выберите список участников",
                    "--file-filter=*.xlsx",
                ],
                capture_output=True,
                text=True,
            )
            if dialog.returncode == 1:
                return
            if dialog.returncode != 0:
                messagebox.showerror(
                    "Не удалось открыть выбор файла",
                    dialog.stderr.strip(),
                    parent=self.root,
                )
                return
            path = dialog.stdout.strip()
        else:
            path = filedialog.askopenfilename(
                parent=self.root,
                title="Выберите список участников",
                filetypes=[("Excel", "*.xlsx")],
            )
        if path:
            self.clear_result()
            self.file_path.set(path)
            self.status.set(f"Выбран файл: {Path(path).name}")

    def clear_result(self):
        self.result = None
        self.result_tree.delete(*self.result_tree.get_children())
        self.save_button.configure(state="disabled")

    def add_hall(self):
        name = self.hall_name.get().strip()
        try:
            capacity = int(self.hall_capacity.get())
            if not name or capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Проверьте зал",
                "Укажите название и положительное число мест.",
                parent=self.root,
            )
            return
        if any(
            self.hall_tree.item(item, "values")[1].casefold() == name.casefold()
            for item in self.hall_tree.get_children()
        ):
            messagebox.showwarning(
                "Зал уже существует", "Используйте другое название.", parent=self.root
            )
            return
        try:
            Hall.create_hall(name, capacity)
            self.selected_halls.add(name)
            self.refresh_halls()
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Не удалось добавить зал", str(exc), parent=self.root)
            return
        self.hall_name.set("")
        self.hall_capacity.set("")
        self.clear_result()
        self.status.set(f"Добавлен зал «{name}»")

    def delete_hall(self):
        selected = self.hall_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Выберите зал", "Выделите зал в списке.", parent=self.root
            )
            return
        name = self.hall_tree.item(selected[0], "values")[1]
        if not messagebox.askyesno(
            "Удалить зал", f"Удалить зал «{name}»?", parent=self.root
        ):
            return
        try:
            next(hall for hall in Hall._all_halls if hall.name == name).delete_hall()
            self.selected_halls.discard(name)
            self.refresh_halls()
        except (OSError, ValueError, KeyError, StopIteration) as exc:
            messagebox.showerror("Не удалось удалить зал", str(exc), parent=self.root)
            return
        self.clear_result()
        self.status.set(f"Удалён зал «{name}»")

    def run_seating(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showwarning(
                "Выберите файл",
                "Сначала выберите Excel со списком участников.",
                parent=self.root,
            )
            return
        try:
            result = main(path, self.selected_halls)
        except Exception as exc:
            messagebox.showerror(
                "Не удалось выполнить рассадку", str(exc), parent=self.root
            )
            return
        self.result = result
        self.result_tree.delete(*self.result_tree.get_children())
        for _, row in result.iterrows():
            tags = ("unseated",) if row["№ компьютера"] == " -" else ()
            self.result_tree.insert(
                "",
                "end",
                values=(
                    row["Фамилия"] + " " + str(row["Имя"]),
                    row["Название школы"],
                    row["Класс обучения"],
                    row["№ компьютера"],
                ),
                tags=tags,
            )
        unseated = int((result["№ компьютера"] == " -").sum())
        self.status.set(
            f"Участников: {len(result)}  ·  Рассажено: {len(result) - unseated}  ·  Без места: {unseated}"
        )
        self.save_button.configure(state="normal")

    def save_result(self):
        if self.result is None:
            return
        if shutil.which("zenity"):
            dialog = subprocess.run(
                [
                    "zenity",
                    "--file-selection",
                    "--save",
                    "--modal",
                    "--title=Сохранить рассадку",
                    "--filename=рассадка.xlsx",
                    "--file-filter=*.xlsx",
                ],
                capture_output=True,
                text=True,
            )
            if dialog.returncode == 1:
                return
            if dialog.returncode != 0:
                messagebox.showerror(
                    "Не удалось выбрать путь", dialog.stderr.strip(), parent=self.root
                )
                return
            path = dialog.stdout.strip()
            if path and Path(path).suffix.lower() != ".xlsx":
                path += ".xlsx"
        else:
            path = filedialog.asksaveasfilename(
                parent=self.root,
                title="Сохранить рассадку",
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
            )
        if not path:
            return
        try:
            self.result.to_excel(path, index=False)
        except (OSError, ValueError, PermissionError) as exc:
            messagebox.showerror(
                "Не удалось сохранить файл", str(exc), parent=self.root
            )
            return
        self.status.set(f"Сохранено: {path}")
        messagebox.showinfo("Готово", "Рассадка сохранена.", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    SeatingApp(root)
    root.mainloop()
