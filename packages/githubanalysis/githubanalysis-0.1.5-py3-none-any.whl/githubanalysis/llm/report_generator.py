from typing import Dict, Any
import json
from datetime import datetime
import os
import re
from githubanalysis.core.enhanced_git_analyzer import EnhancedGitAnalyzer

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, analysis_results: Dict[str, Any], 
                       repository_name: str,
                       format: str = "json") -> str:
        """Generate a comprehensive report from analysis results and an Excel file with commit info."""
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{repository_name}_{timestamp}_report"
        
        # Generate Excel file with commit info
        commits = analysis_results.get('commits', [])
        if commits:
            try:
                import pandas as pd
                excel_data = [
                    {
                        'Commit Hash': c['hash'],
                        'Author': c['author'],
                        'Date': c['date'],
                        'Message': c['message']
                    }
                    for c in commits
                ]
                df = pd.DataFrame(excel_data)
                excel_filename = f"{self.output_dir}/{base_filename}.xlsx"
                df.to_excel(excel_filename, index=False)
            except ImportError:
                print("pandas is not installed. Excel file will not be generated.")
        
        if format.lower() == "markdown":
            # Generate markdown report
            md_content = self._generate_markdown_report(analysis_results)
            filename = f"{self.output_dir}/{base_filename}.md"
            with open(filename, 'w') as f:
                f.write(md_content)
        else:
            # Generate JSON report
            filename = f"{self.output_dir}/{base_filename}.json"
            with open(filename, 'w') as f:
                json.dump(analysis_results, f, indent=2)
        
        return filename

    def _generate_markdown_report(self, report_data: dict) -> str:
        """Generate a markdown formatted report."""
        md = []
        
        # Header
        md.append(f"# Technical Challenges Analysis: {report_data['repository']}")
        md.append(f"\nGenerated at: {report_data['generated_at']}")
        
        # Analysis Period
        if report_data['analysis_period']['start'] or report_data['analysis_period']['end']:
            md.append("\n## Analysis Period")
            period = []
            if report_data['analysis_period']['start']:
                period.append(f"From: {report_data['analysis_period']['start']}")
            if report_data['analysis_period']['end']:
                period.append(f"To: {report_data['analysis_period']['end']}")
            md.append("\n".join(period))
        
        # Technical Challenges (Only)
        if 'llm_analysis' in report_data and report_data['llm_analysis'].get('technical_challenges'):
            md.append("\n## Technical Challenges")
            technical_challenges = report_data['llm_analysis']['technical_challenges']
            # Post-process commit hashes to URLs
            repo_url = report_data.get('repo_url')
            if repo_url:
                analyzer = EnhancedGitAnalyzer(repo_url)
                def repl(match):
                    commit_hash = match.group(1)
                    url = analyzer.get_commit_url(commit_hash)
                    return f'[`{commit_hash}`]({url})'
                # Replace backtick-wrapped hashes of length 7-40
                technical_challenges = re.sub(r'`([0-9a-f]{7,40})`', repl, technical_challenges)
            md.append(technical_challenges)
        
        # Repository Statistics (Last)
        md.append("\n## Repository Statistics")
        md.append(f"- Total Commits: {report_data['total_commits']}")
        md.append(f"- Total Authors: {report_data['total_authors']}")
        md.append(f"- Total Files Changed: {report_data['total_files_changed']}")
        md.append(f"- Total Insertions: {report_data['total_insertions']}")
        md.append(f"- Total Deletions: {report_data['total_deletions']}")
        
        return "\n".join(md) 