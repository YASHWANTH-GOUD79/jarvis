import tkinter as tk
import math
import random
import threading
import time

class JarvisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS AI")
        self.root.geometry("600x700")
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        
        # Main canvas
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Center coordinates
        self.cx = 300
        self.cy = 280
        
        # Animation state
        self.angle = 0
        self.pulse_angle = 0
        self.rings = []
        self.particles = []
        self.status_text = "SYSTEMS ONLINE"
        self.command_text = ""
        self.response_text = ""
        
        # Create initial elements
        self.create_arc_reactor()
        self.create_status_display()
        self.create_command_display()
        
        # Start animations
        self.animate()
        self.update_particles()
        
        # Center window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def create_arc_reactor(self):
        """Create the iconic arc reactor design"""
        # Outer glow
        for i in range(3):
            r = 180 - i * 20
            self.canvas.create_oval(
                self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                outline="#001133", width=30 - i * 8, tags="reactor"
            )
        
        # Main outer ring
        self.canvas.create_oval(
            self.cx - 150, self.cy - 150, self.cx + 150, self.cy + 150,
            outline="#00ffff", width=3, tags="reactor"
        )
        
        # Outer decorative ring
        self.canvas.create_oval(
            self.cx - 140, self.cy - 140, self.cx + 140, self.cy + 140,
            outline="#00aaaa", width=1, tags="reactor"
        )
        
        # Middle ring
        self.canvas.create_oval(
            self.cx - 100, self.cy - 100, self.cx + 100, self.cy + 100,
            outline="#00ffff", width=2, tags="reactor"
        )
        
        # Inner ring
        self.canvas.create_oval(
            self.cx - 60, self.cy - 60, self.cx + 60, self.cy + 60,
            outline="#00dddd", width=1, tags="reactor"
        )
        
        # Core glow
        self.canvas.create_oval(
            self.cx - 30, self.cy - 30, self.cx + 30, self.cy + 30,
            fill="#00ffff", outline="#00ffff", tags="reactor"
        )
        
        # Triangular markers (like the arc reactor)
        self.create_triangular_markers()
        
        # Store ring references for animation
        self.rings = [
            (150, 3, "#00ffff"),
            (140, 1, "#00aaaa"),
            (100, 2, "#00ffff"),
            (60, 1, "#00dddd"),
            (30, 0, "#00ffff")
        ]
    
    def create_triangular_markers(self):
        """Create the triangular markers around the arc reactor"""
        for i in range(6):
            angle = math.radians(i * 60)
            x = self.cx + 165 * math.cos(angle)
            y = self.cy + 165 * math.sin(angle)
            # Triangle pointing inward
            x1 = x + 8 * math.cos(angle)
            y1 = y + 8 * math.sin(angle)
            x2 = x + 15 * math.cos(angle + 0.2)
            y2 = y + 15 * math.sin(angle + 0.2)
            x3 = x + 15 * math.cos(angle - 0.2)
            y3 = y + 15 * math.sin(angle - 0.2)
            self.canvas.create_polygon(
                x1, y1, x2, y2, x3, y3,
                fill="#00ffff", outline="#00aaaa", tags="reactor"
            )
    
    def create_status_display(self):
        """Create status text display"""
        # Status label
        self.canvas.create_text(
            self.cx, 520,
            text="JARVIS",
            fill="#00ffff",
            font=("Courier", 28, "bold"),
            tags="status"
        )
        
        # System status
        self.status_id = self.canvas.create_text(
            self.cx, 560,
            text=self.status_text,
            fill="#00aa00",
            font=("Courier", 12),
            tags="status"
        )
        
        # Version
        self.canvas.create_text(
            self.cx, 580,
            text="v3.0 | IRON MAN SYSTEM",
            fill="#005555",
            font=("Courier", 9),
            tags="status"
        )
    
    def create_command_display(self):
        """Create command/response display"""
        # Command label
        self.canvas.create_text(
            50, 620,
            text=">",
            fill="#00ffff",
            font=("Courier", 12),
            tags="command"
        )
        
        # Command text
        self.command_id = self.canvas.create_text(
            70, 620,
            text="",
            fill="#ffffff",
            font=("Courier", 11),
            tags="command"
        )
    
    def update_state(self, state):
        """Update JARVIS state display"""
        state_colors = {
            "LISTENING": "#00ff00",
            "PROCESSING": "#ffff00", 
            "SPEAKING": "#00ffff",
            "IDLE": "#005555"
        }
        self.status_text = state + " | SYSTEMS ONLINE"
        if hasattr(self, 'status_id'):
            color = state_colors.get(state, "#00aa00")
            self.canvas.itemconfig(self.status_id, fill=color, text=self.status_text)
    
    def show_output(self, text):
        """Display command/response"""
        if hasattr(self, 'command_id'):
            self.canvas.itemconfig(self.command_id, text=text[-50:] if len(text) > 50 else text)
    
    def animate(self):
        """Main animation loop"""
        self.canvas.delete("reactor")
        
        # Pulsing core
        self.pulse_angle += 0.05
        pulse = 25 + 8 * math.sin(self.pulse_angle)
        
        # Outer glow rings
        for i in range(3):
            r = 180 - i * 20
            alpha = int(30 + 20 * math.sin(self.pulse_angle + i * 0.5))
            color = f"#{alpha:02x}{alpha:02x}{alpha:02x}" if alpha < 256 else "#00ffff"
            self.canvas.create_oval(
                self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                outline=color, width=30 - i * 8, tags="reactor"
            )
        
        # Main outer ring with rotation
        self.angle += 0.5
        for i in range(60):
            angle = math.radians(i * 6 + self.angle)
            x = self.cx + 150 * math.cos(angle)
            y = self.cy + 150 * math.sin(angle)
            size = 3 if i % 2 == 0 else 2
            color = "#00ffff" if i % 3 == 0 else "#008888"
            self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=color, outline="", tags="reactor"
            )
        
        # Middle ring dots
        for i in range(12):
            angle = math.radians(i * 30 - self.angle * 0.5)
            x = self.cx + 100 * math.cos(angle)
            y = self.cy + 100 * math.sin(angle)
            self.canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill="#00ffff", outline="", tags="reactor"
            )
        
        # Inner ring
        for i in range(6):
            angle = math.radians(i * 60 + self.angle * 0.3)
            x = self.cx + 60 * math.cos(angle)
            y = self.cy + 60 * math.sin(angle)
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill="#00aaaa", outline="", tags="reactor"
            )
        
        # Pulsing core
        colors = ["#ffffff", "#00ffff", "#00cccc"]
        for i, c in enumerate(colors):
            r = pulse - i * 8
            if r > 0:
                self.canvas.create_oval(
                    self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                    fill=c, outline="", tags="reactor"
                )
        
        # Triangular markers
        for i in range(6):
            angle = math.radians(i * 60)
            x = self.cx + 165 * math.cos(angle)
            y = self.cy + 165 * math.sin(angle)
            x1 = x + 8 * math.cos(angle)
            y1 = y + 8 * math.sin(angle)
            x2 = x + 15 * math.cos(angle + 0.2)
            y2 = y + 15 * math.sin(angle + 0.2)
            x3 = x + 15 * math.cos(angle - 0.2)
            y3 = y + 15 * math.sin(angle - 0.2)
            brightness = int(200 + 55 * math.sin(self.pulse_angle + i))
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            self.canvas.create_polygon(
                x1, y1, x2, y2, x3, y3,
                fill=color, outline="#00aaaa", tags="reactor"
            )
        
        # Update status
        self.canvas.itemconfig(self.status_id, text=self.status_text)
        
        # Update command
        self.canvas.itemconfig(self.command_id, text=self.command_text)
        
        # Schedule next frame
        self.root.after(30, self.animate)
    
    def update_particles(self):
        """Update floating particles"""
        # Add new particle occasionally
        if random.random() < 0.1:
            self.particles.append({
                'x': random.randint(50, 550),
                'y': 650,
                'vy': random.uniform(-2, -0.5),
                'life': 100
            })
        
        # Update existing particles
        for p in self.particles[:]:
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        self.root.after(50, self.update_particles)
    
    def update_status(self, text):
        """Update the status text"""
        self.status_text = text
    
    def show_output(self, text):
        """Show command/response"""
        self.command_text = text
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()