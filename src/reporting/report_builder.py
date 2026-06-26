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
            plot_bgcolor="#0A0F1C",
            paper_bgcolor="#0A0F1C",
            font=dict(color="#F8FAFC", family="Inter"),
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

    def plot_topic_radar(self, subject: str | None = None) -> str:
        """Radar chart of mastery across topics."""
        topics = self.db.weak_topics.get_weakest(limit=20)
        if subject and subject != "All":
            topics = [t for t in topics if t.subject == subject]
            
        if not topics:
            return self._create_empty_html("No mastery data for radar chart.")

        names = [t.topic[:20] + "..." if len(t.topic)>20 else t.topic for t in topics]
        scores = [t.mastery_score * 100 for t in topics]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=names,
            fill='toself',
            name='Mastery',
            line_color="#8B5CF6",
            fillcolor="rgba(139, 92, 246, 0.4)"
        ))

        fig.update_layout(
            title="Knowledge Mastery Radar",
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#273449", color="#94A3B8"),
                angularaxis=dict(gridcolor="#273449", color="#F8FAFC")
            ),
            showlegend=False,
            **self.layout_template
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

    def plot_question_types(self, subject: str | None = None) -> str:
        """Bar chart of average score by question type."""
        exams = self.db.exams.get_all(limit=100)
        if subject and subject != "All":
            exams = [e for e in exams if e.subject == subject]
            
        from collections import defaultdict
        type_scores: dict[str, list[float]] = defaultdict(list)
        
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

        color_palette = ["#58A6FF", "#F78166", "#3FB950", "#A371F7", "#D29922"]
        colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]
        fig = go.Figure(data=[go.Bar(
            x=labels, y=averages,
            text=[f"{v:.1f}%" for v in averages],
            textposition='auto',
            marker_color=colors
        )])
        
        fig.update_layout(
            title="Accuracy by Question Type",
            yaxis=dict(title="Avg Score (%)", range=[0, 100], gridcolor="#30363D"),
            **self.layout_template
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
