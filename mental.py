import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
import datetime
from typing import Dict, List, Any
import os


class MentalHealthTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mental Health Tracker")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_widgets()
        
        # Load data on startup
        self.refresh_data()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect('mental_health_data.db')
        self.cursor = self.conn.cursor()
        
        # Create mood entries table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood_score INTEGER NOT NULL,
                energy_level INTEGER NOT NULL,
                sleep_hours REAL,
                stress_level INTEGER,
                anxiety_level INTEGER,
                notes TEXT,
                activities TEXT,
                triggers TEXT,
                medications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create goals table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                target_date TEXT,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Create the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_mood_entry_tab()
        self.create_history_tab()
        self.create_goals_tab()
        self.create_insights_tab()
        self.create_export_tab()
    
    def create_mood_entry_tab(self):
        """Create the mood entry tab"""
        self.mood_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mood_frame, text="Daily Entry")
        
        # Main container with padding
        main_container = ttk.Frame(self.mood_frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="Daily Mental Health Check-in", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Date selection
        date_frame = ttk.Frame(main_container)
        date_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(date_frame, text="Date:").pack(side='left')
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side='left', padx=(10, 0))
        
        # Mood score (1-10)
        mood_frame = ttk.LabelFrame(main_container, text="Mood Assessment", padding=15)
        mood_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(mood_frame, text="Overall Mood (1=Very Low, 10=Excellent):").pack(anchor='w')
        self.mood_var = tk.IntVar(value=5)
        self.mood_scale = ttk.Scale(mood_frame, from_=1, to=10, variable=self.mood_var, 
                                   orient='horizontal', length=400)
        self.mood_scale.pack(fill='x', pady=5)
        self.mood_label = ttk.Label(mood_frame, text="5")
        self.mood_label.pack()
        self.mood_scale.configure(command=self.update_mood_label)
        
        # Energy level
        ttk.Label(mood_frame, text="Energy Level (1=Exhausted, 10=Energetic):").pack(anchor='w', pady=(15, 0))
        self.energy_var = tk.IntVar(value=5)
        self.energy_scale = ttk.Scale(mood_frame, from_=1, to=10, variable=self.energy_var, 
                                     orient='horizontal', length=400)
        self.energy_scale.pack(fill='x', pady=5)
        self.energy_label = ttk.Label(mood_frame, text="5")
        self.energy_label.pack()
        self.energy_scale.configure(command=self.update_energy_label)
        
        # Sleep hours
        sleep_frame = ttk.Frame(mood_frame)
        sleep_frame.pack(fill='x', pady=(15, 0))
        ttk.Label(sleep_frame, text="Hours of Sleep:").pack(side='left')
        self.sleep_var = tk.StringVar(value="8")
        sleep_spinbox = ttk.Spinbox(sleep_frame, from_=0, to=24, textvariable=self.sleep_var, 
                                   width=5, increment=0.5)
        sleep_spinbox.pack(side='left', padx=(10, 0))
        
        # Stress and anxiety levels
        levels_frame = ttk.Frame(mood_frame)
        levels_frame.pack(fill='x', pady=(15, 0))
        
        stress_frame = ttk.Frame(levels_frame)
        stress_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(stress_frame, text="Stress Level (1-10):").pack()
        self.stress_var = tk.IntVar(value=5)
        stress_scale = ttk.Scale(stress_frame, from_=1, to=10, variable=self.stress_var, 
                                orient='horizontal', length=180)
        stress_scale.pack()
        
        anxiety_frame = ttk.Frame(levels_frame)
        anxiety_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(anxiety_frame, text="Anxiety Level (1-10):").pack()
        self.anxiety_var = tk.IntVar(value=5)
        anxiety_scale = ttk.Scale(anxiety_frame, from_=1, to=10, variable=self.anxiety_var, 
                                 orient='horizontal', length=180)
        anxiety_scale.pack()
        
        # Activities
        activities_frame = ttk.LabelFrame(main_container, text="Activities & Notes", padding=15)
        activities_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        ttk.Label(activities_frame, text="Activities (comma-separated):").pack(anchor='w')
        self.activities_var = tk.StringVar()
        activities_entry = ttk.Entry(activities_frame, textvariable=self.activities_var)
        activities_entry.pack(fill='x', pady=(5, 15))
        
        ttk.Label(activities_frame, text="Triggers/Stressors:").pack(anchor='w')
        self.triggers_var = tk.StringVar()
        triggers_entry = ttk.Entry(activities_frame, textvariable=self.triggers_var)
        triggers_entry.pack(fill='x', pady=(5, 15))
        
        ttk.Label(activities_frame, text="Medications:").pack(anchor='w')
        self.medications_var = tk.StringVar()
        medications_entry = ttk.Entry(activities_frame, textvariable=self.medications_var)
        medications_entry.pack(fill='x', pady=(5, 15))
        
        ttk.Label(activities_frame, text="Additional Notes:").pack(anchor='w')
        self.notes_text = tk.Text(activities_frame, height=4, wrap='word')
        self.notes_text.pack(fill='both', expand=True, pady=5)
        
        # Save button
        save_btn = ttk.Button(main_container, text="Save Entry", command=self.save_entry)
        save_btn.pack(pady=10)
    
    def create_history_tab(self):
        """Create the history viewing tab"""
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        
        # Controls frame
        controls_frame = ttk.Frame(self.history_frame)
        controls_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(controls_frame, text="View History:").pack(side='left')
        refresh_btn = ttk.Button(controls_frame, text="Refresh", command=self.refresh_history)
        refresh_btn.pack(side='right')
        
        # History treeview
        tree_frame = ttk.Frame(self.history_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview with scrollbars
        self.history_tree = ttk.Treeview(tree_frame, columns=('Date', 'Mood', 'Energy', 'Sleep', 
                                                              'Stress', 'Anxiety', 'Notes'), 
                                        show='headings', height=15)
        
        # Configure columns
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('Mood', text='Mood')
        self.history_tree.heading('Energy', text='Energy')
        self.history_tree.heading('Sleep', text='Sleep (h)')
        self.history_tree.heading('Stress', text='Stress')
        self.history_tree.heading('Anxiety', text='Anxiety')
        self.history_tree.heading('Notes', text='Notes')
        
        # Configure column widths
        self.history_tree.column('Date', width=100)
        self.history_tree.column('Mood', width=50)
        self.history_tree.column('Energy', width=60)
        self.history_tree.column('Sleep', width=70)
        self.history_tree.column('Stress', width=50)
        self.history_tree.column('Anxiety', width=50)
        self.history_tree.column('Notes', width=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.history_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Delete button
        delete_btn = ttk.Button(self.history_frame, text="Delete Selected Entry", 
                               command=self.delete_entry)
        delete_btn.pack(pady=(0, 20))
    
    def create_goals_tab(self):
        """Create the goals management tab"""
        self.goals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.goals_frame, text="Goals")
        
        # Goals input frame
        input_frame = ttk.LabelFrame(self.goals_frame, text="Add New Goal", padding=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(input_frame, text="Goal Title:").pack(anchor='w')
        self.goal_title_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.goal_title_var).pack(fill='x', pady=(5, 15))
        
        ttk.Label(input_frame, text="Description:").pack(anchor='w')
        self.goal_desc_text = tk.Text(input_frame, height=3, wrap='word')
        self.goal_desc_text.pack(fill='x', pady=(5, 15))
        
        ttk.Label(input_frame, text="Target Date (YYYY-MM-DD):").pack(anchor='w')
        self.goal_date_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.goal_date_var).pack(fill='x', pady=(5, 15))
        
        ttk.Button(input_frame, text="Add Goal", command=self.add_goal).pack()
        
        # Goals list frame
        list_frame = ttk.LabelFrame(self.goals_frame, text="Current Goals", padding=15)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Goals treeview
        self.goals_tree = ttk.Treeview(list_frame, columns=('Title', 'Description', 'Target Date', 'Status'), 
                                      show='headings', height=10)
        
        self.goals_tree.heading('Title', text='Title')
        self.goals_tree.heading('Description', text='Description')
        self.goals_tree.heading('Target Date', text='Target Date')
        self.goals_tree.heading('Status', text='Status')
        
        self.goals_tree.column('Title', width=150)
        self.goals_tree.column('Description', width=300)
        self.goals_tree.column('Target Date', width=100)
        self.goals_tree.column('Status', width=100)
        
        self.goals_tree.pack(fill='both', expand=True)
        
        # Goals control buttons
        goals_btn_frame = ttk.Frame(list_frame)
        goals_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(goals_btn_frame, text="Mark Complete", 
                  command=self.complete_goal).pack(side='left', padx=(0, 10))
        ttk.Button(goals_btn_frame, text="Delete Goal", 
                  command=self.delete_goal).pack(side='left')
        ttk.Button(goals_btn_frame, text="Refresh", 
                  command=self.refresh_goals).pack(side='right')
    
    def create_insights_tab(self):
        """Create the insights and analytics tab"""
        self.insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.insights_frame, text="Insights")
        
        # Analytics frame
        analytics_frame = ttk.LabelFrame(self.insights_frame, text="Mental Health Analytics", padding=20)
        analytics_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.insights_text = tk.Text(analytics_frame, wrap='word', state='disabled')
        self.insights_text.pack(fill='both', expand=True)
        
        # Refresh button
        ttk.Button(self.insights_frame, text="Generate Insights", 
                  command=self.generate_insights).pack(pady=20)
    
    def create_export_tab(self):
        """Create the data export tab"""
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Export")
        
        export_container = ttk.Frame(self.export_frame)
        export_container.pack(expand=True)
        
        ttk.Label(export_container, text="Export Your Data", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Button(export_container, text="Export to JSON", 
                  command=self.export_to_json).pack(pady=10)
        ttk.Button(export_container, text="Export to CSV", 
                  command=self.export_to_csv).pack(pady=10)
    
    def update_mood_label(self, value):
        """Update mood scale label"""
        self.mood_label.config(text=str(int(float(value))))
    
    def update_energy_label(self, value):
        """Update energy scale label"""
        self.energy_label.config(text=str(int(float(value))))
    
    def save_entry(self):
        """Save a new mood entry to the database"""
        try:
            # Get values from the form
            date = self.date_var.get()
            mood_score = self.mood_var.get()
            energy_level = self.energy_var.get()
            sleep_hours = float(self.sleep_var.get())
            stress_level = self.stress_var.get()
            anxiety_level = self.anxiety_var.get()
            notes = self.notes_text.get("1.0", tk.END).strip()
            activities = self.activities_var.get()
            triggers = self.triggers_var.get()
            medications = self.medications_var.get()
            
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
            
            # Insert into database
            self.cursor.execute('''
                INSERT INTO mood_entries 
                (date, mood_score, energy_level, sleep_hours, stress_level, 
                 anxiety_level, notes, activities, triggers, medications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, mood_score, energy_level, sleep_hours, stress_level,
                  anxiety_level, notes, activities, triggers, medications))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Entry saved successfully!")
            
            # Clear form
            self.clear_form()
            self.refresh_history()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format or sleep hours: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")
    
    def clear_form(self):
        """Clear the entry form"""
        self.date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.mood_var.set(5)
        self.energy_var.set(5)
        self.sleep_var.set("8")
        self.stress_var.set(5)
        self.anxiety_var.set(5)
        self.activities_var.set("")
        self.triggers_var.set("")
        self.medications_var.set("")
        self.notes_text.delete("1.0", tk.END)
    
    def refresh_history(self):
        """Refresh the history treeview"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Fetch data from database
        self.cursor.execute('''
            SELECT date, mood_score, energy_level, sleep_hours, stress_level, 
                   anxiety_level, notes FROM mood_entries ORDER BY date DESC
        ''')
        
        for row in self.cursor.fetchall():
            # Truncate notes if too long
            notes = row[6][:50] + "..." if len(row[6]) > 50 else row[6]
            self.history_tree.insert('', 'end', values=(
                row[0], row[1], row[2], row[3], row[4], row[5], notes
            ))
    
    def delete_entry(self):
        """Delete selected history entry"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            item = self.history_tree.item(selection[0])
            date = item['values'][0]
            
            self.cursor.execute('DELETE FROM mood_entries WHERE date = ?', (date,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Entry deleted successfully!")
            self.refresh_history()
    
    def add_goal(self):
        """Add a new goal"""
        title = self.goal_title_var.get().strip()
        description = self.goal_desc_text.get("1.0", tk.END).strip()
        target_date = self.goal_date_var.get().strip()
        
        if not title:
            messagebox.showwarning("Warning", "Please enter a goal title.")
            return
        
        try:
            if target_date:
                datetime.datetime.strptime(target_date, "%Y-%m-%d")
            
            self.cursor.execute('''
                INSERT INTO goals (title, description, target_date)
                VALUES (?, ?, ?)
            ''', (title, description, target_date or None))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Goal added successfully!")
            
            # Clear form
            self.goal_title_var.set("")
            self.goal_desc_text.delete("1.0", tk.END)
            self.goal_date_var.set("")
            
            self.refresh_goals()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add goal: {e}")
    
    def refresh_goals(self):
        """Refresh the goals treeview"""
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)
        
        self.cursor.execute('''
            SELECT id, title, description, target_date, completed FROM goals 
            ORDER BY completed, target_date
        ''')
        
        for row in self.cursor.fetchall():
            status = "Completed" if row[4] else "In Progress"
            description = row[2][:100] + "..." if len(row[2]) > 100 else row[2]
            self.goals_tree.insert('', 'end', values=(
                row[1], description, row[3] or "No target", status
            ), tags=(str(row[0]),))
    
    def complete_goal(self):
        """Mark selected goal as complete"""
        selection = self.goals_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to complete.")
            return
        
        goal_id = self.goals_tree.item(selection[0])['tags'][0]
        
        self.cursor.execute('UPDATE goals SET completed = 1 WHERE id = ?', (goal_id,))
        self.conn.commit()
        
        messagebox.showinfo("Success", "Goal marked as completed!")
        self.refresh_goals()
    
    def delete_goal(self):
        """Delete selected goal"""
        selection = self.goals_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this goal?"):
            goal_id = self.goals_tree.item(selection[0])['tags'][0]
            
            self.cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Goal deleted successfully!")
            self.refresh_goals()
    
    def generate_insights(self):
        """Generate insights based on historical data"""
        self.insights_text.config(state='normal')
        self.insights_text.delete("1.0", tk.END)
        
        try:
            # Get basic statistics
            self.cursor.execute('''
                SELECT COUNT(*), AVG(mood_score), AVG(energy_level), AVG(sleep_hours),
                       AVG(stress_level), AVG(anxiety_level), MIN(date), MAX(date)
                FROM mood_entries
            ''')
            stats = self.cursor.fetchone()
            
            if stats[0] == 0:
                self.insights_text.insert(tk.END, "No data available for analysis.\n")
                self.insights_text.config(state='disabled')
                return
            
            # Basic statistics
            self.insights_text.insert(tk.END, "=== MENTAL HEALTH INSIGHTS ===\n\n")
            self.insights_text.insert(tk.END, f"Analysis Period: {stats[6]} to {stats[7]}\n")
            self.insights_text.insert(tk.END, f"Total Entries: {stats[0]}\n\n")
            
            self.insights_text.insert(tk.END, "AVERAGES:\n")
            self.insights_text.insert(tk.END, f"• Mood Score: {stats[1]:.1f}/10\n")
            self.insights_text.insert(tk.END, f"• Energy Level: {stats[2]:.1f}/10\n")
            self.insights_text.insert(tk.END, f"• Sleep Hours: {stats[3]:.1f} hours\n")
            self.insights_text.insert(tk.END, f"• Stress Level: {stats[4]:.1f}/10\n")
            self.insights_text.insert(tk.END, f"• Anxiety Level: {stats[5]:.1f}/10\n\n")
            
            # Mood trends
            self.cursor.execute('''
                SELECT date, mood_score FROM mood_entries 
                ORDER BY date DESC LIMIT 7
            ''')
            recent_moods = self.cursor.fetchall()
            
            if len(recent_moods) >= 2:
                trend = "improving" if recent_moods[0][1] > recent_moods[-1][1] else "declining"
                self.insights_text.insert(tk.END, f"RECENT TREND: Your mood appears to be {trend} "
                                                 f"over the last {len(recent_moods)} entries.\n\n")
            
            # Sleep correlation
            self.cursor.execute('''
                SELECT sleep_hours, AVG(mood_score) as avg_mood
                FROM mood_entries
                WHERE sleep_hours IS NOT NULL
                GROUP BY ROUND(sleep_hours)
                ORDER BY avg_mood DESC
                LIMIT 3
            ''')
            sleep_data = self.cursor.fetchall()
            
            if sleep_data:
                self.insights_text.insert(tk.END, "SLEEP INSIGHTS:\n")
                self.insights_text.insert(tk.END, f"• Best mood with ~{sleep_data[0][0]} hours of sleep\n")
                if len(sleep_data) > 1:
                    self.insights_text.insert(tk.END, f"• Good mood also with ~{sleep_data[1][0]} hours\n")
                self.insights_text.insert(tk.END, "\n")
            
            # Goal progress
            self.cursor.execute('SELECT COUNT(*), SUM(completed) FROM goals')
            goal_stats = self.cursor.fetchone()
            
            if goal_stats[0] > 0:
                completion_rate = (goal_stats[1] or 0) / goal_stats[0] * 100
                self.insights_text.insert(tk.END, f"GOAL PROGRESS:\n")
                self.insights_text.insert(tk.END, f"• {goal_stats[1] or 0} of {goal_stats[0]} goals completed ")
                self.insights_text.insert(tk.END, f"({completion_rate:.1f}%)\n\n")
            
            # Recommendations
            self.insights_text.insert(tk.END, "RECOMMENDATIONS:\n")
            
            if stats[1] < 6:  # Low mood
                self.insights_text.insert(tk.END, "• Consider activities that boost your mood\n")
            if stats[3] < 7:  # Low sleep
                self.insights_text.insert(tk.END, "• Aim for more sleep (7-9 hours recommended)\n")
            if stats[4] > 6:  # High stress
                self.insights_text.insert(tk.END, "• Practice stress reduction techniques\n")
            if stats[5] > 6:  # High anxiety
                self.insights_text.insert(tk.END, "• Consider anxiety management strategies\n")
            
            self.insights_text.insert(tk.END, "• Continue tracking for better insights\n")
            self.insights_text.insert(tk.END, "• Consult healthcare providers for persistent concerns\n")
            
        except Exception as e:
            self.insights_text.insert(tk.END, f"Error generating insights: {e}")
        
        self.insights_text.config(state='disabled')
    
    def export_to_json(self):
        """Export data to JSON format"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Export mood entries
            self.cursor.execute('SELECT * FROM mood_entries')
            mood_columns = [description[0] for description in self.cursor.description]
            mood_data = [dict(zip(mood_columns, row)) for row in self.cursor.fetchall()]
            
            # Export goals
            self.cursor.execute('SELECT * FROM goals')
            goal_columns = [description[0] for description in self.cursor.description]
            goal_data = [dict(zip(goal_columns, row)) for row in self.cursor.fetchall()]
            
            export_data = {
                'export_date': datetime.datetime.now().isoformat(),
                'mood_entries': mood_data,
                'goals': goal_data
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def export_to_csv(self):
        """Export mood entries to CSV format"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            self.cursor.execute('''
                SELECT date, mood_score, energy_level, sleep_hours, stress_level,
                       anxiety_level, activities, triggers, medications, notes
                FROM mood_entries ORDER BY date
            ''')
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Mood Score', 'Energy Level', 'Sleep Hours',
                               'Stress Level', 'Anxiety Level', 'Activities', 
                               'Triggers', 'Medications', 'Notes'])
                writer.writerows(self.cursor.fetchall())
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def refresh_data(self):
        """Refresh all data views"""
        self.refresh_history()
        self.refresh_goals()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    app = MentalHealthTracker()
    app.run()
