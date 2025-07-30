"""Command-line interface for credit-risk-creditum."""

import argparse
import json
import sys
from typing import Dict, Any
from pathlib import Path

from .core.application import CreditApplication
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog='credit-risk',
        description='Credit Risk Assessment CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assess individual credit risk
  credit-risk assess --type individual --data '{"credit_score": 720, "monthly_income": 5000, "monthly_debt": 1500, "loan_amount": 25000, "loan_purpose": "home"}'
  
  # Assess corporate credit risk
  credit-risk assess --type corporate --data '{"years_in_business": 5, "annual_revenue": 500000, "industry": "tech", "loan_amount": 100000, "loan_purpose": "expansion"}'
  
  # Run stress tests
  credit-risk stress-test --type individual --data '{"credit_score": 720, "monthly_income": 5000, "monthly_debt": 1500, "loan_amount": 25000, "loan_purpose": "home"}'
  
  # Load application data from file
  credit-risk assess --type individual --file application.json
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'credit-risk-creditum {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Assess command
    assess_parser = subparsers.add_parser('assess', help='Assess credit risk')
    assess_parser.add_argument(
        '--type',
        choices=['individual', 'corporate'],
        required=True,
        help='Type of credit application'
    )
    assess_parser.add_argument(
        '--data',
        type=str,
        help='Application data as JSON string'
    )
    assess_parser.add_argument(
        '--file',
        type=Path,
        help='Path to JSON file containing application data'
    )
    assess_parser.add_argument(
        '--economic-data',
        type=str,
        help='Economic indicators as JSON string'
    )
    assess_parser.add_argument(
        '--output',
        choices=['json', 'table', 'summary'],
        default='summary',
        help='Output format'
    )
    
    # Stress test command
    stress_parser = subparsers.add_parser('stress-test', help='Run stress tests')
    stress_parser.add_argument(
        '--type',
        choices=['individual', 'corporate'],
        required=True,
        help='Type of credit application'
    )
    stress_parser.add_argument(
        '--data',
        type=str,
        help='Application data as JSON string'
    )
    stress_parser.add_argument(
        '--file',
        type=Path,
        help='Path to JSON file containing application data'
    )
    stress_parser.add_argument(
        '--scenarios',
        nargs='*',
        choices=['recession', 'inflation_surge', 'market_crash', 'optimistic'],
        help='Specific scenarios to test (default: all)'
    )
    stress_parser.add_argument(
        '--output',
        choices=['json', 'table', 'summary'],
        default='summary',
        help='Output format'
    )
    
    # Scenarios command
    scenarios_parser = subparsers.add_parser('scenarios', help='List available stress test scenarios')
    scenarios_parser.add_argument(
        '--output',
        choices=['json', 'table'],
        default='table',
        help='Output format'
    )
    
    return parser


def load_application_data(args) -> Dict[str, Any]:
    """Load application data from CLI arguments or file."""
    if args.file:
        try:
            with open(args.file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.data:
        try:
            return json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON data: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Either --data or --file must be provided.", file=sys.stderr)
        sys.exit(1)


def load_economic_data(economic_data_str: str) -> Dict[str, Any]:
    """Load economic data from JSON string."""
    if not economic_data_str:
        return {}
    
    try:
        return json.loads(economic_data_str)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid economic data JSON: {e}", file=sys.stderr)
        sys.exit(1)


def format_assessment_output(decision: Dict[str, Any], output_format: str) -> str:
    """Format assessment decision output."""
    if output_format == 'json':
        return json.dumps(decision, indent=2)
    elif output_format == 'table':
        lines = [
            "Credit Risk Assessment Results",
            "=" * 30,
            f"Decision: {decision['decision'].upper()}",
            f"Risk Score: {decision.get('risk_score', 'N/A'):.3f}",
            f"Risk Category: {decision.get('risk_category', 'N/A')}",
            f"Max Loan Amount: ${decision.get('max_loan_amount', 0):,.0f}",
            f"Economic Factor: {decision.get('economic_factor', 'N/A'):.3f}"
        ]
        if 'stress_scenario' in decision:
            lines.append(f"Stress Scenario: {decision['stress_scenario']}")
        return '\n'.join(lines)
    else:  # summary
        risk_score = decision.get('risk_score', 0)
        emoji = "✅" if decision['decision'] == 'approved' else "❌"
        return f"{emoji} {decision['decision'].upper()} | Risk: {risk_score:.3f} | Max Amount: ${decision.get('max_loan_amount', 0):,.0f}"


def format_stress_test_output(results: Dict[str, Any], output_format: str) -> str:
    """Format stress test results output."""
    if output_format == 'json':
        return json.dumps(results, indent=2)
    elif output_format == 'table':
        lines = [
            "Stress Test Results",
            "=" * 20,
            f"Baseline Decision: {results['baseline_decision']['decision'].upper()}",
            f"Baseline Risk Score: {results['baseline_decision'].get('risk_score', 0):.3f}",
            "",
            "Scenario Results:",
            "-" * 16
        ]
        
        for scenario_name, scenario_result in results['scenario_results'].items():
            decision = scenario_result['decision']
            change_indicator = "📈" if scenario_result['decision_change'] else "📊"
            lines.append(f"{change_indicator} {scenario_name}: {decision['decision'].upper()} (Risk: {decision.get('risk_score', 0):.3f})")
        
        lines.extend([
            "",
            "Summary:",
            f"Decision Changes: {results['summary']['decision_changes']}/{len(results['scenario_results'])}",
            f"Worst Case Risk: {results['summary']['worst_case_risk_score']:.3f}",
            f"Best Case Risk: {results['summary']['best_case_risk_score']:.3f}",
            f"Stable Decision: {'Yes' if results['summary']['stable_decision'] else 'No'}"
        ])
        
        return '\n'.join(lines)
    else:  # summary
        summary = results['summary']
        stability_emoji = "🟢" if summary['stable_decision'] else "🟡"
        return f"{stability_emoji} Tested {len(results['scenario_results'])} scenarios | Changes: {summary['decision_changes']} | Risk Range: {summary['best_case_risk_score']:.3f}-{summary['worst_case_risk_score']:.3f}"


def format_scenarios_output(scenarios: list, output_format: str) -> str:
    """Format stress test scenarios output."""
    if output_format == 'json':
        return json.dumps(scenarios, indent=2)
    else:  # table
        lines = [
            "Available Stress Test Scenarios",
            "=" * 32,
            ""
        ]
        
        for scenario in scenarios:
            lines.extend([
                f"🔥 {scenario['name']} - {scenario['title']}",
                f"   {scenario['description']}",
                ""
            ])
        
        return '\n'.join(lines)


def cmd_assess(args) -> None:
    """Handle assess command."""
    # Load application data
    application_data = load_application_data(args)
    
    # Initialize credit application
    app = CreditApplication()
    
    # Load economic data if provided
    if args.economic_data:
        economic_data = load_economic_data(args.economic_data)
        app.economic_indicators.update_indicators(economic_data)
    
    # Make decision
    try:
        decision = app.make_decision(application_data, args.type)
        output = format_assessment_output(decision, args.output)
        print(output)
    except Exception as e:
        print(f"Error during assessment: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_stress_test(args) -> None:
    """Handle stress-test command."""
    # Load application data
    application_data = load_application_data(args)
    
    # Initialize credit application
    app = CreditApplication()
    
    # Run stress tests
    try:
        results = app.run_stress_tests(application_data, args.type)
        
        # Filter scenarios if specified
        if args.scenarios:
            filtered_results = {
                k: v for k, v in results['scenario_results'].items()
                if k in args.scenarios
            }
            results['scenario_results'] = filtered_results
            
            # Recalculate summary for filtered results
            if filtered_results:
                decision_changes = sum(1 for r in filtered_results.values() if r['decision_change'])
                worst_case = max((r['decision']['risk_score'] or 0) for r in filtered_results.values())
                best_case = min((r['decision']['risk_score'] or 0) for r in filtered_results.values())
                stable = all(not r['decision_change'] for r in filtered_results.values())
                
                results['summary'].update({
                    'decision_changes': decision_changes,
                    'worst_case_risk_score': worst_case,
                    'best_case_risk_score': best_case,
                    'stable_decision': stable
                })
        
        output = format_stress_test_output(results, args.output)
        print(output)
    except Exception as e:
        print(f"Error during stress testing: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_scenarios(args) -> None:
    """Handle scenarios command."""
    app = CreditApplication()
    scenarios = app.get_stress_scenarios()
    output = format_scenarios_output(scenarios, args.output)
    print(output)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'assess':
        cmd_assess(args)
    elif args.command == 'stress-test':
        cmd_stress_test(args)
    elif args.command == 'scenarios':
        cmd_scenarios(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()