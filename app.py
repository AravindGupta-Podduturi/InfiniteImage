import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps, ImageDraw

APP = "Infinite Image"
VER = "1.3.0"
BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#687386"
BORDER = "#DDE3EC"
ACCENT = "#315EFB"
SIDE = "#111827"
ACTIVE = "#24314A"
DARK_BG = "#10141C"
DARK_CARD = "#171D27"
DARK_TEXT = "#F4F7FB"
DARK_MUTED = "#AAB5C5"
DARK_BORDER = "#2A3444"

FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "BMP": ".bmp", "TIFF": ".tiff", "GIF": ".gif", "ICO": ".ico"}
IMAGE_TYPES = [("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.gif *.ico")]


class ScrollableFrame(tk.Frame):
    """Small themed vertical scrolling container used for settings panels."""
    def __init__(self, parent, bg, dark=False, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas)
        self.canvas.bind_all("<MouseWheel>", self._wheel, add="+")
        self.canvas.bind_all("<Button-4>", self._wheel_linux, add="+")
        self.canvas.bind_all("<Button-5>", self._wheel_linux, add="+")

    def _on_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _wheel(self, event):
        try:
            if self.winfo_containing(event.x_root, event.y_root) is not None:
                self.canvas.yview_scroll(int(-event.delta / 120), "units")
        except Exception:
            pass

    def _wheel_linux(self, event):
        try:
            self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
        except Exception:
            pass


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP)
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.dark = False
        self.files = []
        self.photo = None
        self.preview_photo = None
        self.page = "Home"

        self.fmt = tk.StringVar(value="PNG")
        self.quality = tk.DoubleVar(value=90)
        self.preset = tk.StringVar(value="Original")
        self.width = tk.StringVar()
        self.height = tk.StringVar()
        self.keep = tk.BooleanVar(value=True)
        self.shape = tk.StringVar(value="Original")
        self.limit = tk.StringVar(value="No limit")
        self.outdir = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.preview_info = tk.StringVar(value="No image selected")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        self.build_shell()
        self.home()

    def configure_styles(self):
        self.style.configure("TButton", font=("Segoe UI", 10), padding=(13, 8))
        self.style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(15, 9), foreground="white", background=ACCENT)
        self.style.map("Primary.TButton", background=[("active", "#2447C8")])

    def build_shell(self):
        self.side = tk.Frame(self.root, bg=SIDE, width=230)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)

        brand = tk.Frame(self.side, bg=SIDE)
        brand.pack(fill="x", padx=16, pady=(18, 22))
        self.logo_label = tk.Label(brand, bg=SIDE)
        self.logo_label.pack(side="left")
        self.load_logo()
        tk.Label(brand, text=APP, bg=SIDE, fg="white", font=("Segoe UI Semibold", 15)).pack(side="left", padx=10)

        self.nav = {}
        for name, sym in [("Home", "⌂"), ("Convert", "⇄"), ("Resize", "↗"), ("Batch", "▦")]:
            b = tk.Button(
                self.side,
                text=f"  {sym}   {name}",
                anchor="w",
                bg=SIDE,
                fg="white",
                activebackground=ACTIVE,
                activeforeground="white",
                relief="flat",
                bd=0,
                font=("Segoe UI", 11),
                padx=18,
                pady=12,
                command=lambda n=name: self.go(n),
            )
            b.pack(fill="x", padx=10, pady=2)
            self.nav[name] = b

        tk.Frame(self.side, bg=SIDE).pack(fill="both", expand=True)
        tk.Label(self.side, text="●  Local processing", bg=SIDE, fg="#76D6AA", font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=18)
        tk.Label(self.side, text="Your images stay on this PC.", bg=SIDE, fg="#AEB8C7", font=("Segoe UI", 8)).pack(anchor="w", padx=18, pady=(3, 12))
        for text, cmd in [("☾  Theme", self.toggle), ("ⓘ  About", self.about)]:
            tk.Button(self.side, text=text, anchor="w", bg=SIDE, fg="#AEB8C7", activebackground=ACTIVE, activeforeground="white", relief="flat", bd=0, font=("Segoe UI", 10), padx=18, pady=8, command=cmd).pack(fill="x", padx=10)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main, bg=BG, height=78)
        self.header.pack(fill="x", padx=30, pady=(20, 0))
        self.header.pack_propagate(False)
        self.title = tk.Label(self.header, bg=BG, fg=TEXT, font=("Segoe UI Semibold", 23))
        self.title.pack(anchor="w")
        self.sub = tk.Label(self.header, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.sub.pack(anchor="w")
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=(8, 18))
        self.statusbar = tk.Frame(self.main, bg=CARD, height=34, highlightbackground=BORDER, highlightthickness=1)
        self.statusbar.pack(fill="x", side="bottom")
        tk.Label(self.statusbar, textvariable=self.status, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=7)

    def load_logo(self):
        logo_path = Path(__file__).with_name("infinite_image_logo.png")
        if logo_path.exists():
            try:
                im = Image.open(logo_path).convert("RGBA")
                im.thumbnail((48, 48), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(im)
                self.logo_label.configure(image=self.logo_photo, width=50, height=50)
                return
            except Exception:
                pass
        # Fallback icon if the supplied logo is unavailable.
        c = tk.Canvas(self.logo_label, width=44, height=44, bg=SIDE, highlightthickness=0)
        c.create_oval(3, 3, 41, 41, fill=ACCENT, outline="")
        c.create_text(22, 22, text="∞", fill="white", font=("Segoe UI Semibold", 25))
        c.pack()

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)

    def go(self, name):
        self.page = name
        self.nav_active(name)
        {"Home": self.home, "Convert": self.convert, "Resize": self.resize, "Batch": self.batch}[name]()

    def nav_active(self, name):
        for k, b in self.nav.items():
            b.configure(bg=ACTIVE if k == name else SIDE)

    def head(self, title, subtitle):
        self.title.configure(text=title)
        self.sub.configure(text=subtitle)

    def add(self):
        chosen = filedialog.askopenfilenames(title="Select images", filetypes=IMAGE_TYPES)
        if chosen:
            self.files = list(dict.fromkeys(self.files + list(chosen)))
            self.status.set(f"{len(self.files)} image(s) selected")
            if hasattr(self, "lst"):
                self.refresh()
            if hasattr(self, "action_button"):
                self.update_action_label()

    def refresh(self):
        self.lst.delete(0, "end")
        for p in self.files:
            try:
                with Image.open(p) as im:
                    detail = f"{im.width} × {im.height}  •  {im.format or Path(p).suffix.upper().replace('.', '')}"
            except Exception:
                detail = "Unreadable image"
            self.lst.insert("end", f"{Path(p).name}   •   {detail}")
        if self.files:
            self.lst.selection_set(0)
            self.preview(self.files[0])
        else:
            self.preview(None)

    def remove(self):
        selected = list(self.lst.curselection())
        for i in reversed(selected):
            self.files.pop(i)
        self.refresh()
        if hasattr(self, "action_button"):
            self.update_action_label()
        self.status.set(f"{len(self.files)} image(s) selected" if self.files else "Ready")

    def clear_files(self):
        self.files = []
        self.refresh()
        if hasattr(self, "action_button"):
            self.update_action_label()
        self.status.set("Ready")

    def select(self, _event=None):
        selected = self.lst.curselection()
        if selected:
            self.preview(self.files[selected[0]])

    def preview(self, path):
        if not path:
            self.preview_photo = None
            if hasattr(self, "pl"):
                self.pl.configure(image="", text="No image selected")
            self.preview_info.set("No image selected")
            return
        try:
            with Image.open(path) as source:
                im = ImageOps.exif_transpose(source).convert("RGBA")
                original_size = im.size
                im.thumbnail((360, 230), Image.Resampling.LANCZOS)

                # Paint transparent images over a subtle checkerboard, then a neutral card.
                canvas = Image.new("RGBA", (380, 250), "#EEF1F5")
                checker = Image.new("RGBA", (380, 250), "#EEF1F5")
                cd = ImageDraw.Draw(checker)
                step = 16
                for y in range(0, 250, step):
                    for x in range(0, 380, step):
                        if ((x // step) + (y // step)) % 2:
                            cd.rectangle((x, y, x + step, y + step), fill="#E3E7ED")
                canvas.alpha_composite(checker)
                x = (380 - im.width) // 2
                y = (250 - im.height) // 2
                canvas.alpha_composite(im, (x, y))
                self.preview_photo = ImageTk.PhotoImage(canvas)
                self.pl.configure(image=self.preview_photo, text="", width=380, height=250)
                self.preview_info.set(f"{Path(path).name}  •  {original_size[0]} × {original_size[1]}")
        except Exception as exc:
            self.pl.configure(image="", text="Preview unavailable")
            self.preview_info.set(f"Could not preview image: {exc}")

    def out(self):
        if self.outdir.get().strip():
            folder = Path(self.outdir.get().strip())
        elif self.files:
            folder = Path(self.files[0]).parent
        else:
            folder = Path.home() / "Pictures"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def output_control(self, parent):
        tk.Label(parent, text="Output folder for batch jobs", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(4, 4))
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=18)
        ttk.Entry(row, textvariable=self.outdir).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=lambda: self.outdir.set(filedialog.askdirectory() or self.outdir.get())).pack(side="left", padx=(6, 0))
        tk.Label(parent, text="For one image, the Convert/Resize button opens a Save As window so you can name the output file.", bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=330, justify="left").pack(anchor="w", padx=18, pady=(7, 2))

    def combo(self, parent, label, values, variable):
        tk.Label(parent, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(3, 4))
        ttk.Combobox(parent, values=values, textvariable=variable, state="readonly").pack(fill="x", padx=18, pady=(0, 9))

    def scale(self, parent, label, variable):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=18)
        tk.Label(row, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        value = tk.Label(row, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 9))
        value.pack(side="right")
        def update(*_): value.configure(text=f"{int(float(variable.get()))}%")
        variable.trace_add("write", update)
        update()
        ttk.Scale(parent, from_=10, to=100, variable=variable, orient="horizontal").pack(fill="x", padx=18, pady=(0, 9))

    def workspace(self, title, subtitle):
        """Build a workspace with two independently scrollable right-side panels.

        Preview and settings each have their own scrollbar. The primary Save As /
        batch action is pinned to the bottom so it can never disappear below the
        settings content.
        """
        self.head(title, subtitle)
        self.clear()

        left = tk.Frame(self.content, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(self.content, bg=BG, width=420)
        right.pack(side="right", fill="both", padx=(8, 0))
        right.pack_propagate(False)

        # ---------------- Image list ----------------
        c = self.card(left)
        c.pack(fill="both", expand=True)
        top = tk.Frame(c, bg=CARD)
        top.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(top, text="Images", bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 13)).pack(side="left")
        ttk.Button(top, text="Add images", command=self.add).pack(side="right")
        ttk.Button(top, text="Clear", command=self.clear_files).pack(side="right", padx=(0, 7))

        f = tk.Frame(c, bg=CARD)
        f.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        list_bg = "#202734" if self.dark else "#FBFCFE"
        self.lst = tk.Listbox(
            f, bg=list_bg, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            relief="flat", highlightbackground=BORDER, highlightcolor=ACCENT,
            highlightthickness=1, font=("Segoe UI", 10), activestyle="none"
        )
        self.lst.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(f, orient="vertical", command=self.lst.yview)
        scroll.pack(side="right", fill="y")
        self.lst.configure(yscrollcommand=scroll.set)
        self.lst.bind("<<ListboxSelect>>", self.select)

        # ---------------- Fixed action bar ----------------
        # Pack this FIRST with side=bottom so it always gets reserved space.
        action = self.card(right)
        action.pack(fill="x", side="bottom", pady=(8, 0))
        self.action_button = ttk.Button(action, text="Save As…", style="Primary.TButton", command=lambda: None)
        self.action_button.pack(fill="x", padx=14, pady=(10, 7))
        self.action_hint = tk.Label(
            action,
            text="Add an image to begin.",
            bg=CARD, fg=MUTED, font=("Segoe UI", 8),
            wraplength=370, justify="center"
        )
        self.action_hint.pack(fill="x", padx=12, pady=(0, 10))

        # ---------------- Scrollable Preview ----------------
        # This has its OWN scrollbar and can be scrolled independently from settings.
        preview_scroll = ScrollableFrame(right, BG, self.dark, height=270)
        preview_scroll.pack(fill="x", expand=False)
        preview_scroll.pack_propagate(False)
        preview_card = self.card(preview_scroll.inner)
        preview_card.pack(fill="x")
        tk.Label(
            preview_card, text="Preview", bg=CARD, fg=TEXT,
            font=("Segoe UI Semibold", 13)
        ).pack(anchor="w", padx=18, pady=(14, 7))
        self.pl = tk.Label(
            preview_card, text="No image selected", bg="#EEF1F5", fg=MUTED,
            width=380, height=12, anchor="center"
        )
        self.pl.pack(fill="x", padx=14, pady=(0, 5))
        tk.Label(
            preview_card, textvariable=self.preview_info, bg=CARD, fg=MUTED,
            font=("Segoe UI", 8), wraplength=360, justify="center"
        ).pack(fill="x", padx=18, pady=(0, 7))
        ttk.Button(preview_card, text="Remove selected", command=self.remove).pack(anchor="w", padx=18, pady=(0, 12))

        # ---------------- Scrollable Settings ----------------
        settings_holder = tk.Frame(right, bg=BG)
        settings_holder.pack(fill="both", expand=True, pady=(8, 0))
        settings_scroll = ScrollableFrame(settings_holder, BG, self.dark)
        settings_scroll.pack(fill="both", expand=True)
        settings_card = self.card(settings_scroll.inner)
        settings_card.pack(fill="x", pady=(0, 8))
        self.settings_parent = settings_card

        self.refresh()
        self.update_action_label()
        return settings_card

    def update_action_label(self):
        """Keep the primary action visible and make its purpose obvious."""
        if not hasattr(self, "action_button"):
            return
        count = len(self.files)
        if self.page == "Convert":
            if count == 1:
                self.action_button.configure(text="Save As…", command=self.do_convert)
                self.action_hint.configure(text="Choose the exact filename and location for the converted image.")
            elif count > 1:
                self.action_button.configure(text="Convert & Save All  →", command=self.do_convert)
                self.action_hint.configure(text="Multiple images will be saved automatically using _converted names.")
            else:
                self.action_button.configure(text="Save As…", command=self.do_convert)
                self.action_hint.configure(text="Add an image to begin.")
        elif self.page == "Resize":
            if count == 1:
                self.action_button.configure(text="Save As…", command=self.do_resize)
                self.action_hint.configure(text="Choose the exact filename and location for the resized image.")
            elif count > 1:
                self.action_button.configure(text="Resize & Save All  →", command=self.do_resize)
                self.action_hint.configure(text="Multiple images will be saved automatically using _resized names.")
            else:
                self.action_button.configure(text="Save As…", command=self.do_resize)
                self.action_hint.configure(text="Add an image to begin.")

    def save_single_path(self, fmt, operation, source):
        ext = FORMATS[fmt]
        filetypes = [(f"{fmt} image", f"*{ext}"), ("All files", "*.*")]
        default = f"{Path(source).stem}{ext}"
        return filedialog.asksaveasfilename(
            title=f"Save {operation} image as",
            initialfile=default,
            defaultextension=ext,
            filetypes=filetypes,
        )

    def output_paths(self, fmt, operation, suffix):
        if not self.files:
            return []
        if len(self.files) == 1:
            path = self.save_single_path(fmt, operation, self.files[0])
            return [Path(path)] if path else []
        folder = self.out()
        return [folder / f"{Path(src).stem}{suffix}{FORMATS[fmt]}" for src in self.files]

    def home(self):
        self.nav_active("Home")
        self.head("Infinite Image", "Convert, resize and optimize images locally.")
        self.clear()
        h = self.card(self.content)
        h.pack(fill="x")
        tk.Label(h, text="Everything you need for everyday images.", bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(h, text="Convert formats, change dimensions, crop shapes and control file size — without uploading your images.", bg=CARD, fg=MUTED, font=("Segoe UI", 10), wraplength=800, justify="left").pack(anchor="w", padx=24, pady=(0, 20))
        g = tk.Frame(self.content, bg=BG)
        g.pack(fill="x", pady=(14, 0))
        for i, (sym, title, desc, action) in enumerate([
            ("⇄", "Convert format", "JPG, PNG, WEBP, BMP, TIFF, GIF and ICO.", "Convert"),
            ("↗", "Resize image", "Resolution, dimensions, aspect ratios, shapes and size.", "Resize"),
            ("▦", "Batch process", "Apply the same workflow to many images at once.", "Batch"),
        ]):
            c = self.card(g)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 7 if i < 2 else 0))
            g.columnconfigure(i, weight=1)
            tk.Label(c, text=sym, bg=CARD, fg=ACCENT, font=("Segoe UI Semibold", 22)).pack(anchor="w", padx=20, pady=(18, 4))
            tk.Label(c, text=title, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=20)
            tk.Label(c, text=desc, bg=CARD, fg=MUTED, font=("Segoe UI", 9), wraplength=250, justify="left").pack(anchor="w", padx=20, pady=5)
            ttk.Button(c, text="Open →", style="Primary.TButton", command=lambda x=action: self.go(x)).pack(anchor="w", padx=20, pady=(4, 18))
        q = self.card(self.content)
        q.pack(fill="x", pady=(14, 0))
        tk.Label(q, text="Private by design", bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=20, pady=(16, 3))
        tk.Label(q, text="Images are processed locally on your computer. No upload is required.", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(0, 16))

    def convert(self):
        settings = self.workspace("Convert image format", "Change the file type while keeping control over quality and output.")
        tk.Label(settings, text="Conversion settings", bg=CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=18, pady=(16, 12))
        self.combo(settings, "Output format", list(FORMATS), self.fmt)
        self.scale(settings, "Quality", self.quality)
        tk.Label(settings, text="Quality mainly affects JPEG and WEBP. PNG is lossless.",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=350,
                 justify="left").pack(anchor="w", padx=18, pady=(0, 10))
        self.output_control(settings)
        tk.Label(settings, text="Single image: you will be asked for the exact output filename.\nMultiple images: files are saved automatically in the selected output folder.",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=350,
                 justify="left").pack(anchor="w", padx=18, pady=(8, 18))
        self.update_action_label()

    def do_convert(self):
        if not self.files:
            return messagebox.showwarning(APP, "Add at least one image first.")
        fmt = self.fmt.get()
        paths = self.output_paths(fmt, "converted", "_converted")
        if not paths:
            return
        count, errors = 0, []
        for src, dest in zip(self.files, paths):
            try:
                with Image.open(src) as x:
                    im = ImageOps.exif_transpose(x).copy()
                if fmt == "JPEG":
                    if im.mode in ("RGBA", "LA", "P"):
                        im = im.convert("RGBA")
                        bg = Image.new("RGB", im.size, "white")
                        bg.paste(im, mask=im.getchannel("A"))
                        im = bg
                    else:
                        im = im.convert("RGB")
                elif fmt == "GIF":
                    im = im.convert("P")
                elif fmt == "ICO":
                    im.thumbnail((256, 256), Image.Resampling.LANCZOS)
                kwargs = {}
                q = int(float(self.quality.get()))
                if fmt in ("JPEG", "WEBP"):
                    kwargs = {"quality": q, "optimize": True}
                elif fmt == "PNG":
                    kwargs = {"optimize": True}
                im.save(dest, format=fmt, **kwargs)
                count += 1
            except Exception as exc:
                errors.append(f"{Path(src).name}: {exc}")
        self.status.set(f"Converted {count} image(s)")
        if errors:
            messagebox.showwarning(APP, f"{count} converted.\n\n{chr(10).join(errors[:5])}")
        else:
            messagebox.showinfo(APP, f"Successfully converted {count} image(s).")

    def resize(self):
        settings = self.workspace("Resize image", "Set resolution, dimensions, aspect ratio, shape and approximate file size.")
        tk.Label(settings, text="Resize settings", bg=CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=18, pady=(16, 12))
        self.combo(settings, "Dimension preset", ["Original", "HD 1280×720", "Full HD 1920×1080", "2K 2560×1440", "4K 3840×2160", "Instagram Square 1080×1080", "Instagram Portrait 1080×1350", "Story 1080×1920"], self.preset)
        d = tk.Frame(settings, bg=CARD)
        d.pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(d, text="Width", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        tk.Label(d, text="Height", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Entry(d, textvariable=self.width).grid(row=1, column=0, sticky="ew", pady=4)
        ttk.Entry(d, textvariable=self.height).grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        d.columnconfigure(0, weight=1); d.columnconfigure(1, weight=1)
        ttk.Checkbutton(settings, text="Keep aspect ratio", variable=self.keep).pack(anchor="w", padx=18, pady=(2, 8))
        self.combo(settings, "Shape / crop", ["Original", "Square 1:1", "Landscape 4:3", "Landscape 3:2", "Widescreen 16:9", "Portrait 3:4", "Portrait 2:3", "Vertical 9:16", "Circle"], self.shape)
        self.combo(settings, "Approximate maximum file size", ["No limit", "100 KB", "250 KB", "500 KB", "1 MB", "2 MB", "5 MB"], self.limit)
        self.scale(settings, "Quality", self.quality)
        self.output_control(settings)
        tk.Label(settings, text="Single image: Save As lets you choose the exact output name.\nMultiple images: files are saved as *_resized in the selected output folder.",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=350,
                 justify="left").pack(anchor="w", padx=18, pady=(8, 18))
        self.update_action_label()

    def ratio(self):
        return {"Original": None, "Square 1:1": 1, "Landscape 4:3": 4/3, "Landscape 3:2": 3/2, "Widescreen 16:9": 16/9, "Portrait 3:4": 3/4, "Portrait 2:3": 2/3, "Vertical 9:16": 9/16, "Circle": 1}.get(self.shape.get())

    def preset_size(self):
        return {"Original": None, "HD 1280×720": (1280, 720), "Full HD 1920×1080": (1920, 1080), "2K 2560×1440": (2560, 1440), "4K 3840×2160": (3840, 2160), "Instagram Square 1080×1080": (1080, 1080), "Instagram Portrait 1080×1350": (1080, 1350), "Story 1080×1920": (1080, 1920)}.get(self.preset.get())

    def crop(self, im, ratio):
        if not ratio:
            return im
        w, h = im.size; current = w / h
        if current > ratio:
            nw = int(h * ratio); x = (w - nw) // 2; return im.crop((x, 0, x + nw, h))
        if current < ratio:
            nh = int(w / ratio); y = (h - nh) // 2; return im.crop((0, y, w, y + nh))
        return im

    def circle(self, im):
        s = min(im.size)
        im = ImageOps.fit(im, (s, s), method=Image.Resampling.LANCZOS).convert("RGBA")
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
        im.putalpha(mask)
        return im

    def target(self, im):
        w, h = self.width.get().strip(), self.height.get().strip()
        if w.isdigit() or h.isdigit():
            W = int(w) if w.isdigit() else im.width
            H = int(h) if h.isdigit() else im.height
            if self.keep.get():
                if w.isdigit() and not h.isdigit(): H = max(1, round(im.height * W / im.width))
                elif h.isdigit() and not w.isdigit(): W = max(1, round(im.width * H / im.height))
                else:
                    scale = min(W / im.width, H / im.height); W = max(1, round(im.width * scale)); H = max(1, round(im.height * scale))
            return W, H
        return self.preset_size() or im.size

    def save_image(self, im, dest, q):
        ext = dest.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
            im.save(dest, "JPEG", quality=q, optimize=True)
        elif ext == ".webp": im.save(dest, "WEBP", quality=q, method=6)
        elif ext == ".png": im.save(dest, "PNG", optimize=True)
        elif ext == ".bmp": im.convert("RGB").save(dest, "BMP")
        elif ext in (".tif", ".tiff"): im.save(dest, "TIFF", compression="tiff_deflate")
        elif ext == ".gif": im.convert("P").save(dest, "GIF")
        else: im.save(dest)

    def do_resize(self):
        if not self.files:
            return messagebox.showwarning(APP, "Add at least one image first.")
        # Keep the original format for resize. A single image uses Save As so the user chooses the filename.
        if len(self.files) == 1:
            src = self.files[0]
            ext = Path(src).suffix.lower() or ".png"
            fmt = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP", ".bmp": "BMP", ".tif": "TIFF", ".tiff": "TIFF", ".gif": "GIF", ".ico": "ICO"}.get(ext, "PNG")
            path = filedialog.asksaveasfilename(title="Save resized image as", initialfile=f"{Path(src).stem}_resized{ext}", defaultextension=ext, filetypes=[(f"{fmt} image", f"*{ext}"), ("All files", "*.*")])
            if not path:
                return
            paths = [Path(path)]; formats = [fmt]
        else:
            folder = self.out()
            paths = [folder / f"{Path(src).stem}_resized{Path(src).suffix.lower() or '.png'}" for src in self.files]
            formats = ["JPEG" if p.suffix.lower() in (".jpg", ".jpeg") else "PNG" if p.suffix.lower() == ".png" else "WEBP" if p.suffix.lower() == ".webp" else "BMP" if p.suffix.lower() == ".bmp" else "TIFF" if p.suffix.lower() in (".tif", ".tiff") else "GIF" if p.suffix.lower() == ".gif" else "PNG" for p in paths]

        limit = {"No limit": None, "100 KB": 102400, "250 KB": 256000, "500 KB": 512000, "1 MB": 1048576, "2 MB": 2097152, "5 MB": 5242880}[self.limit.get()]
        count, errors = 0, []
        q = int(float(self.quality.get()))
        for src, dest, fmt in zip(self.files, paths, formats):
            try:
                with Image.open(src) as x:
                    im = ImageOps.exif_transpose(x).convert("RGBA" if "A" in x.getbands() else "RGB")
                im = self.crop(im, self.ratio())
                W, H = self.target(im)
                im = ImageOps.contain(im, (W, H), method=Image.Resampling.LANCZOS)
                if self.shape.get() == "Circle":
                    im = self.circle(im)
                self.save_image(im, dest, q)
                if limit and dest.exists() and dest.stat().st_size > limit and dest.suffix.lower() in (".jpg", ".jpeg", ".webp"):
                    for qq in range(q, 19, -10):
                        self.save_image(im, dest, qq)
                        if dest.stat().st_size <= limit: break
                    while dest.stat().st_size > limit and im.width > 200:
                        im = im.resize((max(1, int(im.width * .88)), max(1, int(im.height * .88))), Image.Resampling.LANCZOS)
                        self.save_image(im, dest, 75)
                count += 1
            except Exception as exc:
                errors.append(f"{Path(src).name}: {exc}")
        self.status.set(f"Resized {count} image(s)")
        if errors:
            messagebox.showwarning(APP, f"{count} resized.\n\n{chr(10).join(errors[:5])}")
        else:
            messagebox.showinfo(APP, f"Successfully resized {count} image(s).")

    def batch(self):
        self.head("Batch processing", "Select many images, then choose conversion or resize.")
        self.clear()
        c = self.card(self.content)
        c.pack(fill="both", expand=True)
        tk.Label(c, text="Batch workflow", bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=24, pady=(24, 4))
        tk.Label(c, text="Add multiple images and reuse the same settings across the group.", bg=CARD, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 18))
        ttk.Button(c, text="Add images", command=self.add).pack(anchor="w", padx=24)
        self.lst = tk.Listbox(c, bg="#FBFCFE" if not self.dark else "#202734", fg=TEXT, selectbackground=ACCENT, selectforeground="white", relief="flat", font=("Segoe UI", 10), height=15)
        self.lst.pack(fill="both", expand=True, padx=24, pady=18)
        ttk.Button(c, text="Open Convert →", style="Primary.TButton", command=self.convert).pack(side="left", padx=24, pady=(0, 24))
        ttk.Button(c, text="Open Resize →", command=self.resize).pack(side="left", pady=(0, 24))
        self.refresh()

    def toggle(self):
        global BG, CARD, TEXT, MUTED, BORDER
        self.dark = not self.dark
        if self.dark:
            BG, CARD, TEXT, MUTED, BORDER = DARK_BG, DARK_CARD, DARK_TEXT, DARK_MUTED, DARK_BORDER
        else:
            BG, CARD, TEXT, MUTED, BORDER = "#F5F7FA", "#FFFFFF", "#172033", "#687386", "#DDE3EC"
        self.root.configure(bg=BG)
        self.main.configure(bg=BG); self.header.configure(bg=BG); self.title.configure(bg=BG, fg=TEXT); self.sub.configure(bg=BG, fg=MUTED); self.content.configure(bg=BG)
        self.statusbar.configure(bg=CARD)
        self.go(self.page)

    def about(self):
        messagebox.showinfo(APP, f"{APP} {VER}\n\nA local desktop image conversion and resizing utility.\n\nYour images stay on this computer.")


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default=str(Path(__file__).with_name("app_icon.ico")))
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
