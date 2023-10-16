"""Onboarding Application Extractor Script
"""
import argparse
import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Sequence

import markdown
import pandas as pd
import yaml


@dataclass
class ProjectApplication:
    """Individual Project Application
    """
    paper_summary: str = ''
    issues: str = ''
    contributions: str = ''


class Project(Enum):
    """Project Enumerations
    """
    AID = 'aid'
    BOM = 'bom'
    FS = 'fs'
    MM = 'mm'
    RCT = 'rct'
    SF = 'sf'
    RSG = 'rsg'

@dataclass
class Application:
    """General Application Structure
    """
    timestamp: dt.datetime
    email: str
    permanent_email: str
    first_name: str
    preferred_name: str
    last_name: str
    student_level: str
    expected_graduation: str
    major: str
    minor: str
    institute: str
    adult: str
    resume: str
    estimated_contribution: str
    recording_consent: str
    info_session_attendance: str
    info_session_leads: str
    marketing: str
    llm_use: str
    comments: str
    project_application: Dict[Project, ProjectApplication] = field(default_factory=dict)

with open('project_column_map.yaml', 'r', encoding='ascii') as handle:
    data: Dict = yaml.safe_load(handle)
project_column_map: Dict[Project, Dict[str, str]] = {Project(proj):value
                                                     for proj, value
                                                     in data['projects'].items()}
static_columns: Dict[str, str] = data['static']

def export_apps_to_html(apps: Sequence[Application], directory: Path):
    """Exports application info to html

    Args:
        apps (Sequence[Application]): Applications
        directory (Path): Output directory
    """
    directory.mkdir(parents=True, exist_ok=True)
    for app in apps:
        md_fname = directory.joinpath(f'{app.email.split("@")[0]}_'
                                      f'{app.timestamp.strftime("%Y-%m-%dT%H-%M-%S")}.md')
        html_fname = md_fname.with_suffix('.html')
        md_content = (
            f'Timestamp: {app.timestamp.isoformat()}\n\n'
            f'Email Address: <{app.email}>\n\n'
            f'Permanent Email Address: <{app.permanent_email}>\n\n'
            f'First Name: {app.first_name}\n\n'
            f'Preferred Name/Identifier: {app.preferred_name}\n\n'
            f'Last Name: {app.last_name}\n\n'
            f'Resume: <{app.resume}>\n\n'
            f'Estimated Weekly Contribution: {app.estimated_contribution}\n\n'
            f'Student Level: {app.student_level}\n\n'
            f'Expected Graduation Quarter: {app.expected_graduation}\n\n'
            f'Major: {app.major}\n\n'
            f'Minor: {app.minor}\n\n'
            f'Institute Affiliation: {app.institute}\n\n'
            f'18 or over: {app.adult}\n\n'
            f'Recording Consent: {app.recording_consent}\n\n'
            f'Did applicant use an LLM: {app.llm_use}\n\n'
            f'Did applicant attend info session? {app.info_session_attendance}\n\n'
            f'Which leads did applicant speak with? {app.info_session_leads}\n\n'
            f'How did applicant hear about us? {app.marketing}\n\n'
            f'Applicant comments/feedback: {app.comments}\n\n'
        )
        for proj_name, proj_app in app.project_application.items():
            md_content += f'# {proj_name.name}\n'
            for key, question in project_column_map[proj_name].items():
                md_content += f'## {question}\n'
                md_content += str(getattr(proj_app, key)).replace('\n', '\n\n')
                md_content += '\n\n'

        with open(md_fname, 'w', encoding='utf-8') as handle: # pylint: disable=redefined-outer-name
            # Ignore W0621 redefined outer name due to general context manager name
            handle.write(md_content)

        html_content = markdown.markdown(md_content, extensions=['extra'])
        with open(html_fname, 'w', encoding='utf-8') as handle:
            handle.write(html_content)

def extract_applications(responses: Path, project: Project) -> Sequence[Application]:
    """Extracts the specified project's applications from the CSV

    Args:
        responses (Path): path to CSV
        project (Project): Project to select

    Returns:
        Sequence[Application]: Sequence of application objects
    """
    df = pd.read_csv(responses)
    df['Timestamp'] = [dt.datetime.strptime(val, "%m/%d/%Y %H:%M:%S") for val in df['Timestamp']]
    project_df: pd.DataFrame = df[[*static_columns.values(), *project_column_map[project].values()]]
    project_df: pd.DataFrame = project_df.dropna(axis=0,
                                                 how='all',
                                                 subset=project_column_map[project].values())
    project_df: pd.DataFrame = project_df.fillna('')
    applications: List[Application] = []
    for _, application in project_df.iterrows():
        new_app = Application(
            **{kw:application[key] for kw, key in static_columns.items()}
        )
        new_app.project_application[project] = ProjectApplication(
            **{kw:application[key] for kw, key in project_column_map[project].items()}
        )
        applications.append(new_app)
    return applications

def main():
    """Main application logic
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', choices=[val.value for val in Project], required=True)
    parser.add_argument('-r', '--responses', type=Path, required=True)
    parser.add_argument('-o', '--output_dir', type=Path, required=True)

    args = parser.parse_args()

    responses: Path = args.responses
    if not responses.is_file():
        raise ValueError('Responses file is not a file!')

    output_dir: Path = args.output_dir
    if (output_dir.exists() and not output_dir.is_dir()):
        raise ValueError('Output directory is not a directory!')

    applications = extract_applications(responses, Project(args.project))
    export_apps_to_html(applications, output_dir)


if __name__ == '__main__':
    main()
