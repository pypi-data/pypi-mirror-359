"""
Configuration factory for creating example configurations.

This module handles creation of example configuration files
and directory structures.
"""

import logging
from pathlib import Path
from typing import List
from datetime import datetime


logger = logging.getLogger(__name__)


class ConfigFactory:
    """Creates example configuration files and directory structures."""
    
    def __init__(self, config_root: Path = None):
        """Initialize config factory."""
        self.config_root = config_root or Path("config")
    
    def create_example_configs(self, overwrite: bool = False) -> List[str]:
        """Create example configuration files."""
        created_files = []
        
        # Create directory structure
        directories = [
            "monitoring_groups",
            "user_groups", 
            "reporting_groups",
            # "schedules",  # Removed in v2.2
            "result_display_templates"
        ]
        
        for directory in directories:
            dir_path = self.config_root / directory
            dir_path.mkdir(exist_ok=True, parents=True)
            
            # Create __init__.py
            init_file = dir_path / "__init__.py"
            if not init_file.exists() or overwrite:
                init_file.write_text('"""Configuration group directory."""\n', encoding='utf-8')
                created_files.append(str(init_file))
        
        # Create .env template
        created_files.extend(self._create_env_template(overwrite))
        
        # Create example configurations
        created_files.extend(self._create_monitoring_examples(overwrite))
        created_files.extend(self._create_user_examples(overwrite))
        created_files.extend(self._create_reporting_examples(overwrite))
        # Schedule examples removed in v2.2
        created_files.extend(self._create_template_examples(overwrite))
        
        return created_files
    
    def _create_env_template(self, overwrite: bool = False) -> List[str]:
        """Create .env template file."""
        created_files = []
        
        env_file = self.config_root / ".env"
        if not env_file.exists() or overwrite:
            env_content = """# Telegram API Configuration
TELEGRAM_API_ID=YOUR_API_ID_HERE
TELEGRAM_API_HASH=YOUR_API_HASH_HERE
SESSION_STRING=YOUR_SESSION_STRING_HERE

# Optional: Database path (default: data/statistics.db)
DATABASE_PATH=data/statistics.db
"""
            env_file.write_text(env_content, encoding='utf-8')
            created_files.append(str(env_file))
        
        return created_files
    
    def _create_monitoring_examples(self, overwrite: bool = False) -> List[str]:
        """Create example monitoring group configurations."""
        created_files = []
        
        # Create example monitoring group
        monitoring_example = self.config_root / "monitoring_groups" / "example_monitoring.py"
        if not monitoring_example.exists() or overwrite:
            content = f'''data = {{
    "group_type": "monitoring_group",
    "chat_ids": {{
        -1001234567890: "Example Chat #1",
        -1001234567891: "Example Chat #2",
    }},
    "description": "Example monitoring group",
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            monitoring_example.write_text(content, encoding='utf-8')
            created_files.append(str(monitoring_example))
        
        # Create auto-discovery monitoring group
        monitoring_all = self.config_root / "monitoring_groups" / "all.py"
        if not monitoring_all.exists() or overwrite:
            content = f'''data = {{
    "group_type": "monitoring_group",
    "description": "Auto-discovery of all available chats",
    "auto_discovery": True,
    "filters": {{
        "exclude_private": True,
        "exclude_channels": False,
        "min_members": 2,
    }},
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            monitoring_all.write_text(content, encoding='utf-8')
            created_files.append(str(monitoring_all))
        
        return created_files
    
    def _create_user_examples(self, overwrite: bool = False) -> List[str]:
        """Create example user group configurations."""
        created_files = []
        
        # Create example user group
        user_example = self.config_root / "user_groups" / "example_users.py"
        if not user_example.exists() or overwrite:
            content = f'''data = {{
    "group_type": "user_group",
    "users": {{
        123456789: "John Smith",
        123456790: "Jane Doe",
    }},
    "description": "Example user group",
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            user_example.write_text(content, encoding='utf-8')
            created_files.append(str(user_example))
        
        # Create auto-discovery user group
        user_all = self.config_root / "user_groups" / "all.py"
        if not user_all.exists() or overwrite:
            content = f'''data = {{
    "group_type": "user_group",
    "description": "Auto-discovery of all active users",
    "auto_discovery": True,
    "filters": {{
        "exclude_bots": True,
        "exclude_deleted": True,
        "min_activity": 1,
    }},
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            user_all.write_text(content, encoding='utf-8')
            created_files.append(str(user_all))
        
        return created_files
    
    def _create_reporting_examples(self, overwrite: bool = False) -> List[str]:
        """Create example reporting group configurations."""
        created_files = []
        
        # Create example reporting group
        reporting_example = self.config_root / "reporting_groups" / "example_reports.py"
        if not reporting_example.exists() or overwrite:
            content = f'''data = {{
    "group_type": "reporting_group",
    "chat_ids": {{
        -1001234567893: "Report Chat #1",
        -1001234567894: "Report Chat #2",
    }},
    "description": "Example reporting group",
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            reporting_example.write_text(content, encoding='utf-8')
            created_files.append(str(reporting_example))
        
        # Create auto-discovery reporting group
        reporting_all = self.config_root / "reporting_groups" / "all.py"
        if not reporting_all.exists() or overwrite:
            content = f'''data = {{
    "group_type": "reporting_group",
    "description": "All configured report destination chats",
    "auto_discovery": True,
    "deduplication": True,
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            reporting_all.write_text(content, encoding='utf-8')
            created_files.append(str(reporting_all))
        
        return created_files
    
    # Schedule examples method removed in v2.2
    
    def _create_template_examples(self, overwrite: bool = False) -> List[str]:
        """Create example template configurations."""
        created_files = []
        
        # Create template: from_greatest_to_least
        template_desc = self.config_root / "result_display_templates" / "from_greatest_to_least.py"
        if not template_desc.exists() or overwrite:
            content = f'''data = {{
    "group_type": "template",
    "name": "from_greatest_to_least",
    "description": "Sort by descending activity (most active first)",
    "filters": {{
        "users": {{"min_messages": 1, "show_zero_activity": False}},
        "chats": {{"min_messages": 1, "show_zero_activity": False}}
    }},
    "sorting": {{"users": "desc", "chats": "desc"}},
    "formatting": {{
        "header": "<b><u>{{date}}</u></b>\\n",
        "total": "Total: <code>{{total_messages}}</code>\\n",
        "user_section_header": "\\n<b>Users:</b>\\n",
        "user_line": "{{name}}: <code>{{messages}}</code> - {{percentage:.2f}}%\\n",
        "chat_section_header": "\\n<b>Chats:</b>\\n",
        "chat_line": "{{title}}: <code>{{messages}}</code> - {{percentage:.2f}}%\\n"
    }},
    "options": {{
        "show_percentages": True,
        "round_percentages": 2,
        "telegram_formatting": True,
        "max_message_length": 4096
    }},
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            template_desc.write_text(content, encoding='utf-8')
            created_files.append(str(template_desc))
        
        # Create template: standard_without_filters
        template_standard = self.config_root / "result_display_templates" / "standard_without_filters.py"
        if not template_standard.exists() or overwrite:
            content = f'''data = {{
    "group_type": "template",
    "name": "standard_without_filters",
    "description": "Standard display without filtering (show all users and chats)",
    "filters": {{
        "users": {{"min_messages": 0, "show_zero_activity": True}},
        "chats": {{"min_messages": 0, "show_zero_activity": True}}
    }},
    "sorting": {{"users": "desc", "chats": "desc"}},
    "formatting": {{
        "header": "<b>{{date}}</b>\\n",
        "total": "Total messages: <code>{{total_messages}}</code>\\n",
        "user_section_header": "\\n<b>👥 Users:</b>\\n",
        "user_line": "• {{name}}: <code>{{messages}}</code> ({{percentage:.1f}}%)\\n",
        "chat_section_header": "\\n<b>💬 Chats:</b>\\n",
        "chat_line": "• {{title}}: <code>{{messages}}</code> ({{percentage:.1f}}%)\\n"
    }},
    "options": {{
        "show_percentages": True,
        "round_percentages": 1,
        "telegram_formatting": True,
        "max_message_length": 4096
    }},
    "created_at": "{datetime.now().isoformat()}",
    "updated_at": "{datetime.now().isoformat()}",
}}
'''
            template_standard.write_text(content, encoding='utf-8')
            created_files.append(str(template_standard))
        
        return created_files
    
    def create_directory_structure(self) -> List[str]:
        """Create just the directory structure without example files."""
        created_dirs = []
        
        directories = [
            "monitoring_groups",
            "user_groups", 
            "reporting_groups",
            # "schedules",  # Removed in v2.2
            "result_display_templates"
        ]
        
        for directory in directories:
            dir_path = self.config_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                created_dirs.append(str(dir_path))
        
        return created_dirs 