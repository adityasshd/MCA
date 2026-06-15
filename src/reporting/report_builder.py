"""
report_builder — Plotly Analytics
========================================
Generates interactive Plotly figures based on data queried
from the DatabaseManager. Used by the Analytics UI.
"""

from __future__ import annotations

from typing import Any
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import DatabaseManager

class ReportBuilder:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.layout_template = dict(
            plot_bgcolor="#161B22",
            paper_bgcolor="#161B22",
            font=dict(color="#C9D1D9"),
            margin=dict(l=40, r=40, t=60, b=40)
        )

    def _create_empty_html(self, message: str) -> str:
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#8B949E")
        )
        fig.update_layout(**self.layout_template)
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

    def plot_score_trends(self, subject: str | None = None) -> str:
        """Line chart of exam scores over time."""
        exams = self.db.exams.get_all(limit=100)
        if subject and subject != "All":
            exams = [e for e in exams if e.subject == subject]
        
        if not exams:
            return self._create_empty_html("No exam data available for trends.")

        # Sort chronological
        exams.sort(key=lambda e: e.created_at)
        
        dates = [e.created_at.strftime("%m/%d %H:%M") for e in exams]
        scores = [e.score * 100 if e.score is not None else 0 for e in exams]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=scores, 
            mode='lines+markers',
            marker=dict(color="#58A6FF", size=8),
            line=dict(color="#58A6FF", width=3)
        ))
        
        fig.update_layout(
            title="Exam Score Trends",
            yaxis=dict(title="Score (%)", range=[-5, 105], gridcolor="#30363D"),
            xaxis=dict(gridcolor="#30363D"),
            **self.layout_template
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

    def plot_topic_heatmap(self, subject: str | None = None) -> str:
        """Heatmap of performance by unit."""
        exams = self.db.exams.get_all(limit=100)
        if subject and subject != "All":
            exams = [e for e in exams if e.subject == subject]
            
        if not exams:
            return self._create_empty_html("No data for heatmap.")

        # Aggregate scores by scope (unit)
        unit_scores: dict[str, list[float]] = {}
        for e in exams:
            if e.score is not None:
                if e.scope not in unit_scores:
                    unit_scores[e.scope] = []
                unit_scores[e.scope].append(e.score * 100)
                
        if not unit_scores:
             return self._create_empty_html("No scored exams available.")

        units = list(unit_scores.keys())
        avg_scores = [sum(scores)/len(scores) for scores in unit_scores.values()]
        
        # Convert to 2D array for heatmap
        data = [[s] for s in avg_scores]

        fig = go.Figure(data=go.Heatmap(
            z=data,
            y=units,
            x=["Avg Score"],
            colorscale="RdYlGn",
            zmin=0, zmax=100,
            text=[[f"{s:.1f}%"] for s in avg_scores],
            texttemplate="%{text}",
            showscale=False
        ))
        
        fig.update_layout(
            title="Performance by Topic",
            **self.layout_template
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

    def plot_question_types(self, subject: str | None = None) -> str:
        """Bar chart of average score by question type."""
        exams = self.db.exams.get_all(limit=100)
        if subject and subject != "All":
            exams = [e for e in exams if e.subject == subject]
            
        type_scores: dict[str, list[float]] = {"mcq": [], "short_answer": [], "essay": []}
        
        for e in exams:
            for q in e.questions:
                if q.grade is not None:
                    type_scores[q.type.value].append(q.grade * 100)
                    
        has_data = any(len(v) > 0 for v in type_scores.values())
        if not has_data:
            return self._create_empty_html("No graded questions available.")

        labels = []
        averages = []
        for t, scores in type_scores.items():
            if scores:
                labels.append(t.replace("_", " ").title())
                averages.append(sum(scores) / len(scores))

        colors = ["#58A6FF", "#F78166", "#3FB950"]
        fig = go.Figure(data=[go.Bar(
            x=labels, y=averages,
            text=[f"{v:.1f}%" for v in averages],
            textposition='auto',
            marker_color=colors[:len(labels)]
        )])
        
        fig.update_layout(
            title="Accuracy by Question Type",
            yaxis=dict(title="Avg Score (%)", range=[0, 100], gridcolor="#30363D"),
            **self.layout_template
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
