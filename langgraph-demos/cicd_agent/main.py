#!/usr/bin/env python3
import argparse
import sys
from .graph import run_cicd_agent


def main():
    parser = argparse.ArgumentParser(description='CI/CD Agent for Terraform, Docker, and Helm')
    parser.add_argument(
        'paths',
        nargs='+',
        help='Paths to scan for configuration files'
    )
    parser.add_argument(
        '--max-fix-attempts',
        type=int,
        default=3,
        help='Maximum number of auto-fix attempts (default: 3)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run validations only, skip release'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CI/CD Agent - Terraform | Docker | Helm")
    print("=" * 60)
    print(f"Scanning paths: {', '.join(args.paths)}")
    print(f"Max fix attempts: {args.max_fix_attempts}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)
    
    try:
        result = run_cicd_agent(args.paths, args.max_fix_attempts)
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Status: {result['status']}")
        
        if result['docker_images_built']:
            print(f"Docker images built: {len(result['docker_images_built'])}")
            for img in result['docker_images_built']:
                print(f"  - {img}")
        
        if result['helm_charts_released']:
            print(f"Helm charts released: {len(result['helm_charts_released'])}")
            for chart in result['helm_charts_released']:
                print(f"  - {chart}")
        
        print(f"Terraform applied: {result['terraform_applied']}")
        
        if result['error_message']:
            print(f"\nError: {result['error_message']}")
        
        print("=" * 60)
        
        # Exit with appropriate code
        sys.exit(0 if result['status'] == 'success' else 1)
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
