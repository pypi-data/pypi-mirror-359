#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/weather_productivity.py

import datetime
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from logbuch.core.logger import get_logger


class WeatherCondition(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    CLEAR = "clear"


@dataclass
class WeatherData:
    condition: WeatherCondition
    temperature: float
    humidity: float
    description: str
    location: str
    timestamp: datetime.datetime


@dataclass
class ProductivityRecommendation:
    title: str
    description: str
    task_types: List[str]
    energy_level: str
    focus_rating: int  # 1-10
    creativity_boost: bool
    indoor_preference: bool


class WeatherProductivitySystem:
    def __init__(self):
        self.logger = get_logger("weather_productivity")
        self.current_weather = None
        self.weather_history = []
        
        # Weather-productivity mappings
        self.weather_recommendations = {
            WeatherCondition.SUNNY: ProductivityRecommendation(
                title="☀️ Sunny Day Energy Boost",
                description="Sunny weather increases serotonin and energy levels",
                task_types=["creative", "collaborative", "brainstorming", "meetings"],
                energy_level="high",
                focus_rating=8,
                creativity_boost=True,
                indoor_preference=False
            ),
            WeatherCondition.RAINY: ProductivityRecommendation(
                title="🌧️ Perfect Focus Weather",
                description="Rain creates ideal conditions for deep work and concentration",
                task_types=["deep_work", "coding", "writing", "analysis"],
                energy_level="medium",
                focus_rating=9,
                creativity_boost=False,
                indoor_preference=True
            ),
            WeatherCondition.CLOUDY: ProductivityRecommendation(
                title="☁️ Steady Work Conditions",
                description="Overcast skies provide consistent, distraction-free environment",
                task_types=["routine_tasks", "admin", "planning", "organization"],
                energy_level="medium",
                focus_rating=7,
                creativity_boost=False,
                indoor_preference=True
            ),
            WeatherCondition.STORMY: ProductivityRecommendation(
                title="⛈️ High-Intensity Focus",
                description="Storms can increase focus and urgency for important tasks",
                task_types=["urgent_tasks", "problem_solving", "critical_thinking"],
                energy_level="high",
                focus_rating=10,
                creativity_boost=True,
                indoor_preference=True
            ),
            WeatherCondition.CLEAR: ProductivityRecommendation(
                title="🌟 Crystal Clear Thinking",
                description="Clear skies promote mental clarity and decision-making",
                task_types=["strategic_planning", "decision_making", "goal_setting"],
                energy_level="high",
                focus_rating=8,
                creativity_boost=True,
                indoor_preference=False
            ),
            WeatherCondition.SNOWY: ProductivityRecommendation(
                title="❄️ Cozy Focus Weather",
                description="Snow creates a peaceful, distraction-free environment",
                task_types=["deep_work", "planning", "reflection"],
                energy_level="medium",
                focus_rating=8,
                creativity_boost=False,
                indoor_preference=True
            ),
            WeatherCondition.FOGGY: ProductivityRecommendation(
                title="🌫️ Mysterious Productivity",
                description="Fog can enhance introspection and careful thinking",
                task_types=["analysis", "research", "careful_review"],
                energy_level="low",
                focus_rating=6,
                creativity_boost=False,
                indoor_preference=True
            )
        }
        
        self.logger.debug("Weather Productivity System initialized")
    
    def get_weather_display(self) -> str:
        weather = self._get_current_weather()
        
        if not weather:
            return "🌍 Weather data unavailable"
        
        # Weather icons
        icons = {
            WeatherCondition.SUNNY: "☀️",
            WeatherCondition.CLOUDY: "☁️",
            WeatherCondition.RAINY: "🌧️",
            WeatherCondition.STORMY: "⛈️",
            WeatherCondition.SNOWY: "❄️",
            WeatherCondition.FOGGY: "🌫️",
            WeatherCondition.CLEAR: "🌟"
        }
        
        icon = icons.get(weather.condition, "🌍")
        
        # Create beautiful ASCII-style display
        display = f"""
╭─────────────────────────────────────╮
│  {icon} {weather.condition.value.title()} Weather  │
│                                     │
│  🌡️  Temperature: {weather.temperature:.1f}°C        │
│  💧 Humidity: {weather.humidity:.0f}%           │
│  📍 Location: {weather.location}         │
│  🕐 Updated: {weather.timestamp.strftime('%H:%M')}            │
╰─────────────────────────────────────╯
        """
        
        return display.strip()
    
    def _get_current_weather(self) -> Optional[WeatherData]:
        # Mock weather data - in real implementation, use weather API
        import random
        
        conditions = list(WeatherCondition)
        condition = random.choice(conditions)
        
        weather = WeatherData(
            condition=condition,
            temperature=random.uniform(10, 30),
            humidity=random.uniform(30, 90),
            description=f"{condition.value.title()} conditions",
            location="Your Location",
            timestamp=datetime.datetime.now()
        )
        
        self.current_weather = weather
        return weather
    
    def get_weather_productivity_advice(self) -> Dict[str, Any]:
        weather = self._get_current_weather()
        
        if not weather:
            return {"error": "Weather data unavailable"}
        
        recommendation = self.weather_recommendations.get(weather.condition)
        
        if not recommendation:
            return {"error": "No recommendation available"}
        
        # Generate specific task suggestions
        task_suggestions = self._generate_task_suggestions(recommendation)
        
        # Calculate productivity multiplier
        productivity_multiplier = self._calculate_productivity_multiplier(weather, recommendation)
        
        return {
            "weather": {
                "condition": weather.condition.value,
                "temperature": weather.temperature,
                "description": weather.description,
                "icon": self._get_weather_icon(weather.condition)
            },
            "recommendation": {
                "title": recommendation.title,
                "description": recommendation.description,
                "energy_level": recommendation.energy_level,
                "focus_rating": recommendation.focus_rating,
                "creativity_boost": recommendation.creativity_boost,
                "indoor_preference": recommendation.indoor_preference
            },
            "task_suggestions": task_suggestions,
            "productivity_multiplier": productivity_multiplier,
            "optimal_work_location": "indoors" if recommendation.indoor_preference else "flexible",
            "energy_forecast": self._get_energy_forecast(weather, recommendation)
        }
    
    def _get_weather_icon(self, condition: WeatherCondition) -> str:
        icons = {
            WeatherCondition.SUNNY: "☀️",
            WeatherCondition.CLOUDY: "☁️",
            WeatherCondition.RAINY: "🌧️",
            WeatherCondition.STORMY: "⛈️",
            WeatherCondition.SNOWY: "❄️",
            WeatherCondition.FOGGY: "🌫️",
            WeatherCondition.CLEAR: "🌟"
        }
        return icons.get(condition, "🌍")
    
    def _generate_task_suggestions(self, recommendation: ProductivityRecommendation) -> List[str]:
        suggestions = []
        
        for task_type in recommendation.task_types:
            if task_type == "creative":
                suggestions.extend([
                    "Brainstorm new project ideas",
                    "Work on creative writing or design",
                    "Plan innovative solutions"
                ])
            elif task_type == "deep_work":
                suggestions.extend([
                    "Focus on complex coding problems",
                    "Write detailed documentation",
                    "Analyze data or research"
                ])
            elif task_type == "collaborative":
                suggestions.extend([
                    "Schedule team meetings",
                    "Collaborate on shared projects",
                    "Network and build relationships"
                ])
            elif task_type == "routine_tasks":
                suggestions.extend([
                    "Organize files and workspace",
                    "Process emails and communications",
                    "Update project status and reports"
                ])
            elif task_type == "urgent_tasks":
                suggestions.extend([
                    "Tackle overdue high-priority items",
                    "Resolve critical issues",
                    "Make important decisions"
                ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_productivity_multiplier(self, weather: WeatherData, 
                                         recommendation: ProductivityRecommendation) -> float:
        base_multiplier = 1.0
        
        # Temperature effects
        if 18 <= weather.temperature <= 24:  # Optimal temperature range
            base_multiplier += 0.2
        elif weather.temperature < 10 or weather.temperature > 30:
            base_multiplier -= 0.1
        
        # Humidity effects
        if 40 <= weather.humidity <= 60:  # Optimal humidity
            base_multiplier += 0.1
        elif weather.humidity > 80:
            base_multiplier -= 0.1
        
        # Weather condition effects
        condition_multipliers = {
            WeatherCondition.SUNNY: 1.2,
            WeatherCondition.RAINY: 1.1,  # Good for focus
            WeatherCondition.CLEAR: 1.15,
            WeatherCondition.STORMY: 1.3,  # High intensity
            WeatherCondition.CLOUDY: 1.0,
            WeatherCondition.FOGGY: 0.9,
            WeatherCondition.SNOWY: 0.95
        }
        
        condition_multiplier = condition_multipliers.get(weather.condition, 1.0)
        
        return round(base_multiplier * condition_multiplier, 2)
    
    def _get_energy_forecast(self, weather: WeatherData, 
                           recommendation: ProductivityRecommendation) -> str:
        energy_level = recommendation.energy_level
        
        if energy_level == "high":
            return "⚡ High energy expected - perfect for challenging tasks"
        elif energy_level == "medium":
            return "🔋 Steady energy levels - good for consistent work"
        else:
            return "😴 Lower energy expected - focus on lighter tasks"
    
    def get_weather_dashboard(self) -> Dict[str, Any]:
        weather_display = self.get_weather_display()
        productivity_advice = self.get_weather_productivity_advice()
        
        return {
            "weather_display": weather_display,
            "productivity_advice": productivity_advice,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_weekly_weather_productivity(self) -> List[Dict]:
        # Mock weekly forecast
        weekly_data = []
        
        for i in range(7):
            date = datetime.date.today() + datetime.timedelta(days=i)
            
            # Mock weather for each day
            import random
            condition = random.choice(list(WeatherCondition))
            temp = random.uniform(15, 25)
            
            recommendation = self.weather_recommendations.get(condition)
            
            daily_data = {
                "date": date.isoformat(),
                "day_name": date.strftime("%A"),
                "weather": {
                    "condition": condition.value,
                    "temperature": temp,
                    "icon": self._get_weather_icon(condition)
                },
                "productivity_rating": recommendation.focus_rating if recommendation else 5,
                "recommended_tasks": recommendation.task_types if recommendation else [],
                "energy_level": recommendation.energy_level if recommendation else "medium"
            }
            
            weekly_data.append(daily_data)
        
        return weekly_data


# Export for CLI integration
__all__ = ['WeatherProductivitySystem', 'WeatherData', 'ProductivityRecommendation']
