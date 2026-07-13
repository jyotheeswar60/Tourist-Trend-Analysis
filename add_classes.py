import os
import glob

def add_animation_classes():
    files = glob.glob('pages/*.py')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Add animation classes to specific elements
        content = content.replace('className="page-header"', 'className="page-header animate-on-scroll fade-up"')
        content = content.replace('className="filter-panel"', 'className="filter-panel animate-on-scroll fade-up stagger-1"')
        content = content.replace('className="kpi-grid"', 'className="kpi-grid animate-on-scroll fade-up stagger-1"')
        content = content.replace('className="kpi-card"', 'className="kpi-card animate-on-scroll fade-up"')
        content = content.replace('className="chart-grid"', 'className="chart-grid animate-on-scroll fade-up stagger-2"')
        content = content.replace('className="chart-card"', 'className="chart-card animate-on-scroll fade-up stagger-3"')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

if __name__ == "__main__":
    add_animation_classes()
    print("Animation classes added successfully.")
