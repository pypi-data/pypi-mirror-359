"""
Demo commands showing enhanced timezone UX in statistics collection.

This module demonstrates how the enhanced timezone system integrates
with existing statistics collection commands.
"""

import click
import logging
from datetime import datetime, date
from typing import Optional

from ..core.enhanced_timezone_validator import validate_timezone_interactive
from ..core.timezone_helper import TimezoneHelper


logger = logging.getLogger(__name__)


@click.group(name='demo')
def demo_group():
    """Demo commands for enhanced timezone features."""
    pass


@demo_group.command('collect-stats')
@click.option('--monitoring-group', '-mg', 
              default='all',
              help='Monitoring group to collect statistics for')
@click.option('--target-date', '-d', 
              type=click.DateTime(formats=['%Y-%m-%d']),
              help='Date to collect statistics for (default: today)')
@click.option('--timezone', '-tz',
              help='Timezone for statistics collection (auto-detected if not provided)')
@click.option('--force', '-f', is_flag=True,
              help='Force collection even if data already exists')
@click.option('--interactive', is_flag=True, default=True,
              help='Enable interactive timezone selection')
def demo_collect_stats(monitoring_group: str, 
                      target_date: Optional[datetime],
                      timezone: Optional[str],
                      force: bool,
                      interactive: bool):
    """
    Demo command showing enhanced timezone handling in statistics collection.
    
    This command demonstrates:
    - Auto-detection of system timezone
    - Interactive timezone selection
    - Validation with suggestions
    - Smart error handling
    """
    
    try:
        # Step 1: Resolve timezone with enhanced UX
        click.echo("🌍 Timezone Configuration")
        click.echo("-" * 30)
        
        resolved_timezone = validate_timezone_interactive(timezone) if interactive else timezone
        if not resolved_timezone:
            helper = TimezoneHelper()
            resolved_timezone = helper.detect_system_timezone()
            click.echo(f"🔍 Auto-detected timezone: {resolved_timezone}")
        else:
            click.echo(f"✅ Using timezone: {resolved_timezone}")
        
        # Step 2: Show timezone info
        helper = TimezoneHelper()
        time_info = helper.get_current_time_in_timezone(resolved_timezone)
        click.echo(f"   Current time: {time_info['current_time']}")
        click.echo(f"   UTC offset: {time_info['utc_offset']}")
        if time_info['is_dst']:
            click.echo(f"   🌞 Daylight saving time is active")
        
        # Step 3: Determine target date
        if target_date is None:
            target_date = date.today()
            click.echo(f"\n📅 Using target date: {target_date}")
        else:
            target_date = target_date.date()
            click.echo(f"\n📅 Target date: {target_date}")
        
        # Step 4: Simulate statistics collection
        click.echo(f"\n📊 Collecting Statistics")
        click.echo("-" * 30)
        click.echo(f"   Monitoring group: {monitoring_group}")
        click.echo(f"   Target date: {target_date}")
        click.echo(f"   Timezone: {resolved_timezone}")
        click.echo(f"   Force collection: {force}")
        
        # Simulate processing
        import time
        with click.progressbar(range(5), label='Processing...') as bar:
            for i in bar:
                time.sleep(0.5)
        
        click.echo(f"\n✅ Statistics collection completed!")
        click.echo(f"   📈 Collected data for {monitoring_group} on {target_date}")
        click.echo(f"   🕐 Timezone boundaries: {resolved_timezone}")
        
    except click.Abort:
        click.echo("\n❌ Operation cancelled by user")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        logger.exception("Error in demo stats collection")


@demo_group.command('show-timezone-info')
@click.argument('timezone', required=False)
def show_timezone_info(timezone: Optional[str]):
    """Show detailed information about a timezone (or auto-detect)."""
    try:
        helper = TimezoneHelper()
        
        if timezone:
            click.echo(f"🔍 Timezone Information: {timezone}")
        else:
            timezone = helper.detect_system_timezone()
            click.echo(f"🔍 Auto-detected Timezone: {timezone}")
        
        click.echo("-" * 50)
        
        # Validate and get info
        try:
            resolved = helper.resolve_timezone(timezone)
            time_info = helper.get_current_time_in_timezone(resolved)
            
            click.echo(f"✅ Valid timezone")
            if resolved != timezone:
                click.echo(f"   Original: {timezone}")
                click.echo(f"   Resolved: {resolved}")
            
            click.echo(f"   Current time: {time_info['current_time']}")
            click.echo(f"   UTC offset: {time_info['utc_offset']}")
            click.echo(f"   DST active: {'Yes' if time_info['is_dst'] else 'No'}")
            
            # Show timezone boundaries for today
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone(resolved)
            today = datetime.now(tz).date()
            start_of_day = tz.localize(datetime.combine(today, datetime.min.time()))
            end_of_day = tz.localize(datetime.combine(today, datetime.max.time()))
            
            click.echo(f"\n📅 Today's boundaries in {resolved}:")
            click.echo(f"   Start: {start_of_day.strftime('%Y-%m-%d %H:%M:%S %Z')} ({start_of_day.utctimetuple().tm_hour:02d}:{start_of_day.utctimetuple().tm_min:02d} UTC)")
            click.echo(f"   End:   {end_of_day.strftime('%Y-%m-%d %H:%M:%S %Z')} ({end_of_day.utctimetuple().tm_hour:02d}:{end_of_day.utctimetuple().tm_min:02d} UTC)")
            
        except ValueError as e:
            click.echo(f"❌ Invalid timezone: {e}")
            
            # Show suggestions
            suggestions = helper.suggest_timezone(timezone)
            if suggestions:
                click.echo(f"\n💡 Suggestions:")
                for suggestion in suggestions:
                    click.echo(f"   - {suggestion}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@demo_group.command('quick-collect')
@click.option('--timezone', '-tz', help='Timezone (use aliases like msk, est, pst)')
@click.option('--yesterday', '-y', is_flag=True, help='Collect for yesterday instead of today')
def quick_collect(timezone: Optional[str], yesterday: bool):
    """Quick stats collection with timezone aliases support."""
    try:
        helper = TimezoneHelper()
        
        # Resolve timezone (including aliases)
        if timezone:
            try:
                resolved_tz = helper.resolve_timezone(timezone)
                click.echo(f"🌍 Using timezone: {resolved_tz}")
                if resolved_tz != timezone:
                    click.echo(f"   (resolved from alias: {timezone})")
            except ValueError:
                click.echo(f"❌ Invalid timezone: {timezone}")
                
                # Show available aliases
                click.echo(f"\n🔗 Available aliases:")
                for alias, tz in helper.aliases.items():
                    click.echo(f"   {alias} → {tz}")
                return
        else:
            resolved_tz = helper.detect_system_timezone()
            click.echo(f"🔍 Auto-detected: {resolved_tz}")
        
        # Determine collection type
        collection_type = "yesterday" if yesterday else "today"
        click.echo(f"📊 Quick collection for {collection_type}")
        
        # Show time info
        time_info = helper.get_current_time_in_timezone(resolved_tz)
        click.echo(f"   Current time: {time_info['current_time']}")
        
        # Simulate quick collection
        click.echo("⚡ Starting quick collection...")
        
        import time
        with click.progressbar(range(3), label='Collecting...') as bar:
            for i in bar:
                time.sleep(0.3)
        
        click.echo(f"✅ Quick collection completed for {collection_type}!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@demo_group.command('timezone-test')
def timezone_test():
    """Test timezone system with various inputs."""
    test_cases = [
        "Europe/Moscow",
        "msk",  # alias
        "est",  # alias  
        "Asia/Tokyo",
        "UTC",
        "invalid_timezone",
        "America/New_York",
        "pst"  # alias
    ]
    
    helper = TimezoneHelper()
    
    click.echo("🧪 Timezone System Test")
    click.echo("=" * 40)
    
    for test_tz in test_cases:
        click.echo(f"\n🔍 Testing: {test_tz}")
        try:
            resolved = helper.resolve_timezone(test_tz)
            time_info = helper.get_current_time_in_timezone(resolved)
            
            click.echo(f"   ✅ Valid → {resolved}")
            click.echo(f"   🕐 Time: {time_info['current_time']}")
            
        except ValueError:
            click.echo(f"   ❌ Invalid")
            suggestions = helper.suggest_timezone(test_tz, limit=2)
            if suggestions:
                click.echo(f"   💡 Suggestions: {', '.join(suggestions)}")


# Register commands
def register_demo_commands(cli_group):
    """Register demo commands with the main CLI."""
    cli_group.add_command(demo_group) 