"""
Dynamic content support tools: generate_chart_data, create_data_visualization, 
compute_metrics, generate_timeline, embed_asset.
Empowers Claude to generate dynamic, data-driven slide content.
"""

import json
from typing import TYPE_CHECKING, Union, Dict, Any, List, Optional
from datetime import datetime, date
from pathlib import Path

from ..models import StatusOut
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


# Input models for dynamic content tools
class GenerateChartDataIn(BaseModel):
    """Input for generate_chart_data."""
    chart_type: str = Field(
        ...,
        description="Type of chart (bar, line, pie, doughnut, scatter)"
    )
    labels: List[str] = Field(
        ...,
        description="Labels for the data points"
    )
    datasets: List[Dict[str, Any]] = Field(
        ...,
        description="Dataset(s) with values and metadata"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chart.js options configuration"
    )


class GenerateChartDataOut(BaseModel):
    """Output for generate_chart_data."""
    chart_config: Dict[str, Any] = Field(
        ...,
        description="Complete Chart.js configuration object"
    )
    component_syntax: str = Field(
        ...,
        description="Markdown syntax to embed the chart"
    )


class CreateVisualizationIn(BaseModel):
    """Input for create_data_visualization."""
    viz_type: str = Field(
        ...,
        description="Type of visualization (chart, metrics, timeline, grid)"
    )
    data: Union[Dict[str, Any], List[Any]] = Field(
        ...,
        description="Data for the visualization"
    )
    title: Optional[str] = Field(
        None,
        description="Title for the visualization"
    )
    styling: Dict[str, Any] = Field(
        default_factory=dict,
        description="Styling options (colors, sizes, etc.)"
    )


class ComputeMetricsIn(BaseModel):
    """Input for compute_metrics."""
    calculation_type: str = Field(
        ...,
        description="Type of calculation (sum, average, growth, percentage)"
    )
    values: List[float] = Field(
        ...,
        description="Numeric values for calculation"
    )
    format: str = Field(
        "number",
        description="Output format (number, currency, percentage)"
    )
    decimals: int = Field(
        2,
        description="Number of decimal places"
    )


class MetricsOut(BaseModel):
    """Output for compute_metrics."""
    result: float = Field(..., description="Calculated result")
    formatted: str = Field(..., description="Formatted result string")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (unit, trend, etc.)"
    )


class TimelineEvent(BaseModel):
    """Single timeline event."""
    date: str = Field(..., description="Date in ISO format or relative (e.g., '2024 Q1')")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    icon: Optional[str] = Field(None, description="Icon name")
    color: Optional[str] = Field(None, description="Event color")


class GenerateTimelineIn(BaseModel):
    """Input for generate_timeline."""
    events: List[TimelineEvent] = Field(
        ...,
        description="List of timeline events"
    )
    orientation: str = Field(
        "vertical",
        description="Timeline orientation (vertical, horizontal)"
    )
    style: str = Field(
        "default",
        description="Timeline style (default, minimal, detailed)"
    )


class EmbedAssetIn(BaseModel):
    """Input for embed_asset."""
    asset_type: str = Field(
        ...,
        description="Type of asset (image, icon, logo, diagram)"
    )
    source: str = Field(
        ...,
        description="Asset source (URL, path, or icon name)"
    )
    alt_text: str = Field(
        ...,
        description="Alternative text for accessibility"
    )
    width: Optional[str] = Field(
        None,
        description="Width (e.g., '300px', '50%', 'auto')"
    )
    height: Optional[str] = Field(
        None,
        description="Height (e.g., '200px', 'auto')"
    )
    caption: Optional[str] = Field(
        None,
        description="Caption text"
    )


def register_dynamic_content_tools(mcp: "FastMCP") -> None:
    """Register dynamic content tools with the MCP server."""
    
    @mcp.tool()
    def generate_chart_data(params: Union[GenerateChartDataIn, str, dict]) -> GenerateChartDataOut:
        """Generate properly formatted data for chart components."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = GenerateChartDataIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = GenerateChartDataIn(**params)
        elif not isinstance(params, GenerateChartDataIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Build Chart.js configuration
        chart_config = {
            "type": params.chart_type,
            "data": {
                "labels": params.labels,
                "datasets": params.datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                **params.options
            }
        }
        
        # Apply default colors if not provided
        default_colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
        for i, dataset in enumerate(chart_config["data"]["datasets"]):
            if "backgroundColor" not in dataset and params.chart_type in ["bar", "pie", "doughnut"]:
                dataset["backgroundColor"] = default_colors[:len(params.labels)]
            if "borderColor" not in dataset and params.chart_type in ["line", "scatter"]:
                dataset["borderColor"] = default_colors[i % len(default_colors)]
                dataset["borderWidth"] = 2
        
        # Generate component syntax
        component_syntax = f""":::chart type={params.chart_type}
```json
{json.dumps(chart_config["data"], indent=2)}
```
:::"""
        
        return GenerateChartDataOut(
            chart_config=chart_config,
            component_syntax=component_syntax
        )
    
    @mcp.tool()
    def create_data_visualization(params: Union[CreateVisualizationIn, str, dict]) -> StatusOut:
        """Create a complete data visualization component."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = CreateVisualizationIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = CreateVisualizationIn(**params)
        elif not isinstance(params, CreateVisualizationIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Generate visualization based on type
        if params.viz_type == "metrics":
            # Format metrics data
            metrics_md = ":::metrics\n"
            for item in params.data if isinstance(params.data, list) else [params.data]:
                metrics_md += f"- label: {item.get('label', 'Metric')}\n"
                metrics_md += f"  value: {item.get('value', '0')}\n"
                if 'change' in item:
                    metrics_md += f"  change: {item['change']}\n"
                if 'trend' in item:
                    metrics_md += f"  trend: {item['trend']}\n"
            metrics_md += ":::"
            
            return StatusOut(
                success=True,
                message="Metrics visualization created",
                details={"markdown": metrics_md}
            )
        
        elif params.viz_type == "timeline":
            # Format timeline data
            timeline_md = ":::timeline\n"
            for event in params.data if isinstance(params.data, list) else [params.data]:
                timeline_md += f"- date: {event.get('date', '')}\n"
                timeline_md += f"  title: {event.get('title', '')}\n"
                if 'description' in event:
                    timeline_md += f"  description: {event['description']}\n"
            timeline_md += ":::"
            
            return StatusOut(
                success=True,
                message="Timeline visualization created",
                details={"markdown": timeline_md}
            )
        
        else:
            return StatusOut(
                success=False,
                message=f"Unsupported visualization type: {params.viz_type}"
            )
    
    @mcp.tool()
    def compute_metrics(params: Union[ComputeMetricsIn, str, dict]) -> MetricsOut:
        """Perform calculations for metric displays."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ComputeMetricsIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ComputeMetricsIn(**params)
        elif not isinstance(params, ComputeMetricsIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Perform calculation
        result = 0.0
        metadata = {}
        
        if params.calculation_type == "sum":
            result = sum(params.values)
        elif params.calculation_type == "average":
            result = sum(params.values) / len(params.values) if params.values else 0
        elif params.calculation_type == "growth":
            if len(params.values) >= 2:
                old_val = params.values[0]
                new_val = params.values[-1]
                result = ((new_val - old_val) / old_val * 100) if old_val != 0 else 0
                metadata["trend"] = "up" if result > 0 else "down" if result < 0 else "flat"
        elif params.calculation_type == "percentage":
            if len(params.values) >= 2:
                part = params.values[0]
                whole = params.values[1]
                result = (part / whole * 100) if whole != 0 else 0
        
        # Format result
        if params.format == "currency":
            formatted = f"${result:,.{params.decimals}f}"
        elif params.format == "percentage":
            formatted = f"{result:.{params.decimals}f}%"
        else:
            formatted = f"{result:,.{params.decimals}f}"
        
        return MetricsOut(
            result=result,
            formatted=formatted,
            metadata=metadata
        )
    
    @mcp.tool()
    def generate_timeline(params: Union[GenerateTimelineIn, str, dict]) -> StatusOut:
        """Generate timeline data from event list."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = GenerateTimelineIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = GenerateTimelineIn(**params)
        elif not isinstance(params, GenerateTimelineIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Sort events by date if possible
        try:
            sorted_events = sorted(params.events, key=lambda e: e.date)
        except:
            sorted_events = params.events
        
        # Generate timeline markdown
        timeline_md = f":::timeline orientation={params.orientation} style={params.style}\n"
        for event in sorted_events:
            timeline_md += f"- date: {event.date}\n"
            timeline_md += f"  title: {event.title}\n"
            if event.description:
                timeline_md += f"  description: {event.description}\n"
            if event.icon:
                timeline_md += f"  icon: {event.icon}\n"
            if event.color:
                timeline_md += f"  color: {event.color}\n"
        timeline_md += ":::"
        
        return StatusOut(
            success=True,
            message=f"Generated timeline with {len(params.events)} events",
            details={
                "markdown": timeline_md,
                "event_count": len(params.events)
            }
        )
    
    @mcp.tool()
    def embed_asset(params: Union[EmbedAssetIn, str, dict]) -> StatusOut:
        """Generate markdown for embedding assets in slides."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = EmbedAssetIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = EmbedAssetIn(**params)
        elif not isinstance(params, EmbedAssetIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Generate appropriate markdown based on asset type
        if params.asset_type == "image":
            # Use image component for more control
            image_md = f':::image src="{params.source}" alt="{params.alt_text}"'
            if params.width:
                image_md += f' width="{params.width}"'
            if params.height:
                image_md += f' height="{params.height}"'
            image_md += '\n'
            if params.caption:
                image_md += params.caption
            image_md += '\n:::'
            
            return StatusOut(
                success=True,
                message="Image embed created",
                details={"markdown": image_md}
            )
        
        elif params.asset_type == "icon":
            # Use svg_icon tool reference
            icon_md = f'<!-- Use svg_icon tool with name="{params.source}" -->'
            
            return StatusOut(
                success=True,
                message="Icon reference created",
                details={
                    "markdown": icon_md,
                    "note": "Use svg_icon tool to generate the actual icon"
                }
            )
        
        elif params.asset_type in ["logo", "diagram"]:
            # Standard markdown image
            img_md = f'![{params.alt_text}]({params.source}'
            if params.width or params.height:
                style = []
                if params.width:
                    style.append(f'width: {params.width}')
                if params.height:
                    style.append(f'height: {params.height}')
                img_md += f' "style={"; ".join(style)}"'
            img_md += ')'
            
            if params.caption:
                img_md = f'<figure>\n{img_md}\n<figcaption>{params.caption}</figcaption>\n</figure>'
            
            return StatusOut(
                success=True,
                message=f"{params.asset_type.title()} embed created",
                details={"markdown": img_md}
            )
        
        else:
            return StatusOut(
                success=False,
                message=f"Unsupported asset type: {params.asset_type}"
            )