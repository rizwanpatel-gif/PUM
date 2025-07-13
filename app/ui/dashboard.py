import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
from typing import Dict, List, Any

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { background-color: #0B0F1A !important; }
            .container, .dbc, .dash-bootstrap, .dash-table-container { background-color: #0B0F1A !important; }
            .card, .modal-content, .alert, .dbc-card { background-color: #151B2B !important; border-radius: 18px !important; box-shadow: 0 2px 16px 0 rgba(0,0,0,0.12) !important; border: none !important; }
            .card-body, .dbc-card-body { background-color: #151B2B !important; }
            h1, h2, h3, h4, h5, h6, .card-title, .card-text, .text-center, .text-muted, .form-label, label, .nav-link, .alert, .table, .btn, .btn-link { color: #E5E7EB !important; }
            .text-secondary, .timestamp, .small, small { color: #9CA3AF !important; }
            .btn-primary, .progress-bar { background-color: #3B82F6 !important; border-color: #3B82F6 !important; color: #fff !important; }
            .btn-success, .text-success { background-color: #00FFB3 !important; color: #00FFB3 !important; }
            .btn-warning, .text-warning { background-color: #F6C343 !important; color: #F6C343 !important; }
            .btn-danger, .text-danger { background-color: #FF4C4C !important; color: #FF4C4C !important; }
            .form-control, .input-group-text { background-color: #23263a !important; color: #E5E7EB !important; border-color: #3B82F6 !important; }
            .table { color: #E5E7EB !important; }
            .border-end { border-right: 1px solid #23263a !important; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

API_BASE_URL = "http://localhost:8000/api/v1"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Protocol Upgrade Monitor", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Network Monitoring", className="text-center mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Img(src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/ethereum.svg", style={"height": "24px", "marginRight": "8px", "verticalAlign": "middle", "filter": "invert(1)"}),
                                html.Span("Ethereum", className="card-title", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                dbc.Badge("Live", color="success", className="ms-2", style={"backgroundColor": "#00FFB3", "color": "#151B2B", "fontWeight": "bold"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            html.Div([
                                html.Span("Block 18,000,000", style={"color": "#9CA3AF", "fontSize": "0.95rem"}),
                                html.Span("+3.2%", style={"color": "#00FFB3", "fontWeight": "bold", "marginLeft": "12px"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            dcc.Graph(
                                id="eth-sparkline",
                                config={"displayModeBar": False},
                                figure=go.Figure(
                                    data=[go.Scatter(y=[1,2,2.5,2,3,4], mode="lines", line={"color": "#3B82F6", "width": 2})],
                                    layout=go.Layout(
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        paper_bgcolor="#151B2B",
                                        plot_bgcolor="#151B2B",
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        height=40
                                    )
                                ),
                                style={"height": "40px"}
                            )
                        ])
                    ], style={"marginBottom": "16px"})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Img(src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/polygon.svg", style={"height": "24px", "marginRight": "8px", "verticalAlign": "middle", "filter": "invert(1)"}),
                                html.Span("Polygon", className="card-title", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                dbc.Badge("Live", color="success", className="ms-2", style={"backgroundColor": "#00FFB3", "color": "#151B2B", "fontWeight": "bold"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            html.Div([
                                html.Span("Block 45,000,000", style={"color": "#9CA3AF", "fontSize": "0.95rem"}),
                                html.Span("+1.5%", style={"color": "#00FFB3", "fontWeight": "bold", "marginLeft": "12px"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            dcc.Graph(
                                id="polygon-sparkline",
                                config={"displayModeBar": False},
                                figure=go.Figure(
                                    data=[go.Scatter(y=[1,1.2,1.5,1.7,2,2.7], mode="lines", line={"color": "#3B82F6", "width": 2})],
                                    layout=go.Layout(
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        paper_bgcolor="#151B2B",
                                        plot_bgcolor="#151B2B",
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        height=40
                                    )
                                ),
                                style={"height": "40px"}
                            )
                        ])
                    ], style={"marginBottom": "16px"})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Img(src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/arbitrum.svg", style={"height": "24px", "marginRight": "8px", "verticalAlign": "middle", "filter": "invert(1)"}),
                                html.Span("Arbitrum", className="card-title", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                dbc.Badge("Live", color="success", className="ms-2", style={"backgroundColor": "#00FFB3", "color": "#151B2B", "fontWeight": "bold"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            html.Div([
                                html.Span("Block 10,000,001", style={"color": "#9CA3AF", "fontSize": "0.95rem"}),
                                html.Span("+2.7%", style={"color": "#00FFB3", "fontWeight": "bold", "marginLeft": "12px"})
                            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                            dcc.Graph(
                                id="arbitrum-sparkline",
                                config={"displayModeBar": False},
                                figure=go.Figure(
                                    data=[go.Scatter(y=[1,1.1,1.3,1.6,2,2.5], mode="lines", line={"color": "#3B82F6", "width": 2})],
                                    layout=go.Layout(
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        paper_bgcolor="#151B2B",
                                        plot_bgcolor="#151B2B",
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        height=40
                                    )
                                ),
                                style={"height": "40px"}
                            )
                        ])
                    ], style={"marginBottom": "16px"})
                ], width=4)
            ], className="mb-3"),
            
            html.H5("Recent Events", className="mb-2"),
            html.Div(id="recent-events", className="mb-3"),
            
            html.H5("Protocol Prices", className="mb-2"),
            html.Div(id="price-feeds", className="mb-3"),
            
            dcc.Graph(id="network-activity-chart"),
            
            dbc.Button("Refresh", id="refresh-network", color="primary", className="mt-2")
            
        ], width=4, className="border-end"),
        
        dbc.Col([
            html.H3("Risk Assessment", className="text-center mb-3"),
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="risk-gauge", config={"displayModeBar": False}, style={"height": "220px"}),
                    html.Div("Risk Over Time", style={"color": "#9CA3AF", "fontWeight": "bold", "marginTop": "-10px", "marginBottom": "8px", "fontSize": "1.1rem"}),
                    dcc.Graph(id="risk-over-time-chart", config={"displayModeBar": False}, style={"height": "180px"})
                ])
            ], style={"marginBottom": "18px"}),
            html.H5("Risk Breakdown", className="mb-2", style={"color": "#E5E7EB"}),
            dcc.Graph(id="risk-breakdown-chart", config={"displayModeBar": False}, style={"height": "320px"}),
            html.H5("Recent Upgrades", className="mb-2"),
            html.Div(id="recent-upgrades"),
            html.H5("High Risk Alerts", className="mb-2"),
            html.Div(id="risk-alerts", className="alert alert-danger"),
            dbc.Button("Refresh", id="refresh-risk", color="warning", className="mt-2")
        ], width=4, className="border-end"),
        
        dbc.Col([
            html.H3("Execution Guidance", className="text-center mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Volatility Prediction", className="mb-2", style={"color": "#E5E7EB"}),
                    dcc.Graph(id="volatility-chart", config={"displayModeBar": False}, style={"height": "320px"})
                ])
            ], style={"marginBottom": "18px"}),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Trading Recommendations", className="mb-2", style={"color": "#E5E7EB"}),
                    html.Div(id="trading-recommendations")
                ])
            ], style={"marginBottom": "18px"}),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Portfolio Impact", className="mb-2", style={"color": "#E5E7EB"}),
                    dcc.Graph(id="portfolio-impact-chart", config={"displayModeBar": False}, style={"height": "320px"})
                ])
            ], style={"marginBottom": "18px"}),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Execution Timing", className="mb-2", style={"color": "#E5E7EB"}),
                    html.Div(id="execution-timing")
                ])
            ], style={"marginBottom": "18px"}),
            dbc.Button([
                html.Span("Refresh", style={"color": "#fff"}),
                " Guidance"
            ], id="refresh-guidance", color="success", className="mt-2")
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Analytics", className="text-center mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Risk Distribution", className="mb-2", style={"color": "#E5E7EB"}),
                            dcc.Graph(id="risk-distribution-chart", config={"displayModeBar": False}, style={"height": "320px"})
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Volatility Trends", className="mb-2", style={"color": "#E5E7EB"}),
                            dcc.Graph(id="volatility-trends-chart", config={"displayModeBar": False}, style={"height": "320px"})
                        ])
                    ])
                ], width=6)
            ])
        ])
    ], className="mt-4"),
    
    html.Div(id="network-data", style={"display": "none"}),
    html.Div(id="risk-data", style={"display": "none"}),
    html.Div(id="guidance-data", style={"display": "none"}),
    
    dcc.Interval(
        id="interval-component",
        interval=10*1000,
        n_intervals=0
    ),
    html.Div([
        html.H3("Sentiment Analysis"),
        dcc.Input(id="sentiment-input", type="text", placeholder="Enter text for sentiment analysis", style={"width": "60%"}),
        html.Button(
            "Analyze",
            id="analyze-sentiment-btn",
            n_clicks=0,
            style={
                "backgroundColor": "#2196F3",
                "color": "white",
                "borderRadius": "20px",
                "border": "none",
                "padding": "8px 24px",
                "fontWeight": "bold",
                "marginLeft": "10px"
            }
        ),
        html.Div(id="sentiment-result", style={"marginTop": "1em"})
    ], style={"margin": "2em 0"}),
    html.Div([
        html.H3("Twitter Sentiment Analysis"),
        dcc.Input(id="twitter-query-input", type="text", placeholder="Enter keyword or hashtag", style={"width": "60%"}),
        html.Button(
            "Fetch Tweets",
            id="fetch-twitter-btn",
            n_clicks=0,
            style={
                "backgroundColor": "#2196F3",
                "color": "white",
                "borderRadius": "20px",
                "border": "none",
                "padding": "8px 24px",
                "fontWeight": "bold",
                "marginLeft": "10px"
            }
        ),
        html.Div(id="twitter-sentiment-result", style={"marginTop": "1em"})
    ], style={"margin": "2em 0"})
], fluid=True)


@app.callback(
    [Output("recent-events", "children"),
     Output("network-activity-chart", "figure"),
     Output("network-data", "children")],
    [Input("refresh-network", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_network_data(n_clicks, n_intervals):
    try:
        network_counts = {}
        events_data = []
        for network in ["ethereum", "polygon", "arbitrum"]:
            try:
                response = requests.get(f"{API_BASE_URL}/events/{network}?since_hours=24", timeout=30)
                if response.status_code == 200:
                    events = response.json().get("events", [])
                    network_counts[network.capitalize()] = len(events)
                    events_data.extend(events[:5])
                else:
                    network_counts[network.capitalize()] = 0
            except Exception as e:
                print(f"Error fetching {network} events: {e}")
                network_counts[network.capitalize()] = 0

        events_list = []
        for event in events_data[:10]:
            events_list.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"Block {event.get('block_number', 'N/A')}", className="card-title"),
                        html.P(f"Type: {event.get('event_type', 'N/A')}", className="card-text"),
                        html.Small(f"Time: {event.get('timestamp', 'N/A')}", className="text-muted")
                    ])
                ], className="mb-2")
            )

        activity_data = network_counts
        activity_fig = go.Figure(data=[
            go.Bar(x=list(activity_data.keys()), y=list(activity_data.values()))
        ])
        activity_fig.update_layout(
            title="Network Activity (Last 24h)",
            xaxis_title="Network",
            yaxis_title="Events"
        )

        return events_list, activity_fig, json.dumps(events_data)

    except Exception as e:
        print(f"Error updating network data: {e}")
        return [], go.Figure(), "[]"


@app.callback(
    [Output("risk-gauge", "figure"),
     Output("risk-over-time-chart", "figure"),
     Output("risk-breakdown-chart", "figure"),
     Output("recent-upgrades", "children"),
     Output("risk-alerts", "children"),
     Output("risk-data", "children")],
    [Input("refresh-risk", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_risk_data(n_clicks, n_intervals):
    print("update_risk_data callback fired")
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/bulk-data", timeout=30)
        if response.status_code != 200:
            return go.Figure(), go.Figure(), go.Figure(), [], [], "{}"
        data = response.json()
        risk_scores = data.get("risk_scores", [])
        recent_upgrades = data.get("recent_upgrades", [])
        
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 50
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Score"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3B82F6"},
                'steps': [
                    {'range': [0, 30], 'color': "#00FFB3"},
                    {'range': [30, 70], 'color': "#F6C343"},
                    {'range': [70, 100], 'color': "#FF4C4C"}
                ],
                'threshold': {
                    'line': {'color': "#FF4C4C", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        gauge_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF'
        )
        risk_over_time_fig = go.Figure()
        if risk_scores:
            risk_over_time_fig.add_trace(go.Scatter(
                y=risk_scores[::-1],
                mode="lines+markers",
                line={"color": "#3B82F6", "width": 3},
                marker={"color": "#3B82F6"}
            ))
        risk_over_time_fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="#151B2B",
            plot_bgcolor="#151B2B",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=90
        )
        if risk_scores:
            breakdown_fig = go.Figure(data=[
                go.Pie(
                    labels=["Medium Risk", "Low Risk", "High Risk"],
                    values=[
                        len([r for r in risk_scores if 30 <= r < 70]),
                        len([r for r in risk_scores if r < 30]),
                        len([r for r in risk_scores if r >= 70])
                    ],
                    marker_colors=["#636EFA", "#EF553B", "#00CC96"],
                    textinfo="percent",
                    textfont=dict(color="#E5E7EB", size=16),
                    insidetextorientation="auto",
                    hole=0
                )
            ])
            breakdown_fig.update_layout(
                title="Risk Distribution",
                title_font_color="#E5E7EB",
                paper_bgcolor="#151B2B",
                plot_bgcolor="#151B2B",
                font_color="#E5E7EB",
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(color="#E5E7EB", size=14)
                )
            )
        else:
            breakdown_fig = go.Figure()
        upgrades_list = []
        for upgrade in recent_upgrades[:5]:
            upgrades_list.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(upgrade.get("protocol_name", "Unknown"), className="card-title"),
                        html.P(upgrade.get("title", "No Title"), className="card-text"),
                        html.Small(f"Status: {upgrade.get('status', 'N/A')}", className="text-muted")
                    ])
                ], className="mb-2")
            )
        high_risk_alerts = []
        for i, score in enumerate(risk_scores):
            if score >= 70:
                high_risk_alerts.append(html.Div(f"Upgrade {i+1} is HIGH RISK: {score:.1f}", style={"color": "#FF4C4C", "fontWeight": "bold"}))
        return gauge_fig, risk_over_time_fig, breakdown_fig, upgrades_list, high_risk_alerts, json.dumps(risk_scores)
    except Exception as e:
        print(f"Error updating risk data: {e}")
        return go.Figure(), go.Figure(), go.Figure(), [], [], "{}"


@app.callback(
    [Output("volatility-chart", "figure"),
     Output("trading-recommendations", "children"),
     Output("portfolio-impact-chart", "figure"),
     Output("execution-timing", "children"),
     Output("guidance-data", "children")],
    [Input("refresh-guidance", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_guidance_data(n_clicks, n_intervals):
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/bulk-data", timeout=30)
        if response.status_code != 200:
            return go.Figure(), [], go.Figure(), [], "{}"
        
        data = response.json()
        recent_upgrades = data.get("recent_upgrades", [])
        trading_recommendations = data.get("trading_recommendations", [])
        
        volatility_data = []
        for upgrade in recent_upgrades[:5]:
            if upgrade.get("volatility_prediction"):
                volatility_data.append({
                    "protocol": upgrade.get("protocol_name", "Unknown"),
                    "volatility": upgrade["volatility_prediction"].get("predicted_volatility", 0)
                })
        
        if volatility_data:
            vol_fig = go.Figure(data=[
                go.Bar(
                    x=[d["protocol"] for d in volatility_data],
                    y=[d["volatility"] for d in volatility_data],
                    marker_color="#3B82F6"
                )
            ])
            vol_fig.update_layout(
                title="Predicted Volatility",
                xaxis_title="Protocol",
                yaxis_title="Volatility",
                paper_bgcolor="#151B2B",
                plot_bgcolor="#151B2B",
                font_color="#E5E7EB"
            )
        else:
            vol_fig = go.Figure()
        
        recommendations = []
        for rec in trading_recommendations:
            color_map = {"Low": "#00FFB3", "Medium": "#F6C343", "High": "#FF4C4C"}
            recommendations.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(rec["protocol"], className="card-title"),
                        html.P(rec["recommendation"], className="card-text"),
                        html.Small(
                            f"Risk level: {rec['risk_level']}", 
                            className="text-muted",
                            style={"color": color_map.get(rec["risk_level"], "#9CA3AF")}
                        )
                    ])
                ], className="mb-2")
            )
        
        impact_fig = go.Figure(data=[
            go.Scatter(
                x=["Before", "After"], 
                y=[100, 95], 
                mode="lines+markers",
                line={"color": "#3B82F6", "width": 3},
                marker={"color": "#3B82F6", "size": 10}
            )
        ])
        impact_fig.update_layout(
            title="Portfolio Impact",
            xaxis_title="Timeline",
            yaxis_title="Portfolio Value (%)",
            paper_bgcolor="#151B2B",
            plot_bgcolor="#151B2B",
            font_color="#E5E7EB"
        )
        
        timing_info = [
            html.Div([
                html.Strong("Optimal Entry: ", style={"color": "#3B82F6"}),
                html.Span("Within 24 hours of upgrade", style={"color": "#FFFFFF"})
            ], className="mb-1"),
            html.Div([
                html.Strong("Exit Strategy: ", style={"color": "#3B82F6"}),
                html.Span("Monitor volatility for 7 days", style={"color": "#FFFFFF"})
            ], className="mb-1"),
            html.Div([
                html.Strong("Stop Loss: ", style={"color": "#3B82F6"}),
                html.Span("5% below entry price", style={"color": "#FFFFFF"})
            ])
        ]
        
        return vol_fig, recommendations, impact_fig, timing_info, json.dumps(recent_upgrades)
        
    except Exception as e:
        print(f"Error updating guidance data: {e}")
        return go.Figure(), [], go.Figure(), [], "{}"


@app.callback(
    Output("price-feeds", "children"),
    [Input("refresh-network", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_price_feeds(n_clicks, n_intervals):
    try:
        response = requests.get(f"{API_BASE_URL}/prices/protocols", timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        prices = data.get("prices", {})
        
        price_cards = []
        for token_id, price_data in prices.items():
            price = price_data.get("price", 0)
            change_24h = price_data.get("change_24h", 0)
            volume_24h = price_data.get("volume_24h", 0)
            
            formatted_price = f"${price:.2f}" if price >= 1 else f"${price:.4f}"
            change_text = f"{change_24h:+.2f}%" if change_24h != 0 else "0.00%"
            change_color = "#00FFB3" if change_24h > 0 else "#FF4C4C" if change_24h < 0 else "#9CA3AF"
            
            if volume_24h >= 1e9:
                formatted_volume = f"${volume_24h/1e9:.1f}B"
            elif volume_24h >= 1e6:
                formatted_volume = f"${volume_24h/1e6:.1f}M"
            elif volume_24h >= 1e3:
                formatted_volume = f"${volume_24h/1e3:.1f}K"
            else:
                formatted_volume = f"${volume_24h:.0f}"
            
            card = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6(token_id.upper(), className="card-title", style={"fontWeight": "bold"}),
                        html.Span(formatted_price, style={"fontSize": "1.1rem", "fontWeight": "bold", "color": "#E5E7EB"}),
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "8px"}),
                    html.Div([
                        html.Span(change_text, style={"color": change_color, "fontWeight": "bold"}),
                        html.Span(f"Vol: {formatted_volume}", style={"color": "#9CA3AF", "marginLeft": "12px", "fontSize": "0.9rem"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                ])
            ], style={"marginBottom": "8px", "backgroundColor": "#151B2B", "border": "none"})
            
            price_cards.append(card)
        
        return price_cards
        
    except Exception as e:
        print(f"Error updating price feeds: {e}")
        return []


PROTOCOLS = [
    {"name": "Uniswap V3", "token_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984"},
    {"name": "Aave V3", "token_address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"},
    {"name": "Compound V3", "token_address": "0xc00e94Cb662C3520282E6f5717214004A7f26888"},
    {"name": "Curve Finance", "token_address": "0xD533a949740bb3306d119CC777fa900bA034cd52"},
]

@app.callback(
    [Output("risk-distribution-chart", "figure"),
     Output("volatility-trends-chart", "figure")],
    [Input("interval-component", "n_intervals")]
)
def update_analytics(n_intervals):
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/bulk-data", timeout=30)
        if response.status_code != 200:
            return go.Figure(), go.Figure()
        
        data = response.json()
        risk_distribution = data.get("risk_distribution", {})
        recent_upgrades = data.get("recent_upgrades", [])
        
        if risk_distribution:
            risk_dist_fig = go.Figure(data=[
                go.Bar(
                    x=list(risk_distribution.keys()), 
                    y=list(risk_distribution.values()),
                    marker_color=["#00FFB3", "#F6C343", "#FF4C4C"]
                )
            ])
            risk_dist_fig.update_layout(
                title="Risk Distribution",
                xaxis_title="Risk Level",
                yaxis_title="Number of Upgrades",
                paper_bgcolor="#151B2B",
                plot_bgcolor="#151B2B",
                font_color="#E5E7EB"
            )
        else:
            risk_dist_fig = go.Figure()
        
        vol_fig = go.Figure()
        for protocol in PROTOCOLS:
            response = requests.get(f"{API_BASE_URL}/volatility/history/{protocol['token_address']}?days=30", timeout=30)
            if response.status_code == 200:
                history = response.json().get("history", [])
                if history:
                    x = [datetime.fromisoformat(item["prediction_time"]) for item in history]
                    y = [item["predicted_volatility"] for item in history]
                    vol_fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=protocol["name"]))
        vol_fig.update_layout(
            title="Volatility Trends",
            xaxis_title="Date",
            yaxis_title="Predicted Volatility",
            paper_bgcolor="#151B2B",
            plot_bgcolor="#151B2B",
            font_color="#E5E7EB"
        )
        return risk_dist_fig, vol_fig
        
    except Exception as e:
        print(f"Error updating analytics: {e}")
        return go.Figure(), go.Figure()


@app.callback(
    Output("sentiment-result", "children"),
    Input("analyze-sentiment-btn", "n_clicks"),
    State("sentiment-input", "value")
)
def analyze_sentiment_callback(n_clicks, text):
    if n_clicks and text:
        try:
            response = requests.post(f"{API_BASE_URL}/sentiment/analyze", json={"text": text}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return html.Div([
                    html.P(f"Sentiment: {data['sentiment']}", style={"fontWeight": "bold", "color": "#2196F3"}),
                    html.P(f"Polarity: {data['polarity']:.2f}", style={"color": "#2196F3"}),
                    html.P(f"Subjectivity: {data['subjectivity']:.2f}", style={"color": "#2196F3"})
                ])
            else:
                return "Error analyzing sentiment."
        except Exception as e:
            return f"Error: {e}"
    return ""

@app.callback(
    Output("twitter-sentiment-result", "children"),
    Input("fetch-twitter-btn", "n_clicks"),
    State("twitter-query-input", "value")
)
def twitter_sentiment_callback(n_clicks, query):
    if n_clicks and query:
        try:
            response = requests.get(f"{API_BASE_URL}/sentiment/twitter", params={"query": query, "count": 10}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and data["results"]:
                    return html.Div([
                        html.H5(f"Recent Tweets for '{query}':"),
                        html.Ul([
                            html.Li([
                                html.P(tweet["text"], style={"color": "#2196F3"}),
                                html.P(f"Sentiment: {tweet['sentiment']} (Polarity: {tweet['polarity']:.2f})", style={"fontWeight": "bold", "color": "#2196F3"})
                            ]) for tweet in data["results"]
                        ])
                    ])
                else:
                    return "No tweets found or unable to fetch tweets."
            else:
                return "Error fetching tweets."
        except Exception as e:
            return f"Error: {e}"
    return ""


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050) 