"""Pipeline utilities for Jenkins pipeline creation and validation."""

import re
from typing import Dict, List, Optional, Set, Tuple
from loguru import logger


class PipelineValidator:
    """Validator for Jenkins pipeline scripts."""
    
    # Common Jenkins pipeline tools and their typical usage
    COMMON_TOOLS = {
        'sh', 'bat', 'powershell', 'echo', 'sleep', 'timeout', 'retry',
        'script', 'checkout', 'git', 'svn', 'build', 'publishHTML',
        'archiveArtifacts', 'junit', 'publishTestResults', 'emailext',
        'slackSend', 'withCredentials', 'withEnv', 'dir', 'deleteDir',
        'fileExists', 'readFile', 'writeFile', 'stash', 'unstash',
        'parallel', 'catchError', 'error', 'currentBuild', 'env',
        'params', 'input', 'milestone', 'lock', 'node', 'stage',
        'steps', 'post', 'always', 'success', 'failure', 'unstable',
        'changed', 'fixed', 'regression', 'aborted', 'cleanup'
    }
    
    def __init__(self):
        """Initialize pipeline validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.used_tools: Set[str] = set()
        self.used_shared_libraries: Set[str] = set()
    
    def validate_pipeline_script(self, script: str, pipeline_type: str = 'declarative') -> Dict[str, any]:
        """Validate a Jenkins pipeline script."""
        self.errors.clear()
        self.warnings.clear()
        self.used_tools.clear()
        self.used_shared_libraries.clear()
        
        if not script or not script.strip():
            self.errors.append("Pipeline script cannot be empty")
            return self._get_validation_result()
        
        # Validate based on pipeline type
        if pipeline_type.lower() == 'declarative':
            self._validate_declarative_pipeline(script)
        elif pipeline_type.lower() == 'scripted':
            self._validate_scripted_pipeline(script)
        else:
            self.errors.append(f"Unknown pipeline type: {pipeline_type}")
        
        # Common validations
        self._validate_common_syntax(script)
        self._extract_used_tools(script)
        self._extract_shared_libraries(script)
        
        return self._get_validation_result()
    
    def _validate_declarative_pipeline(self, script: str) -> None:
        """Validate declarative pipeline syntax."""
        if not re.search(r'\bpipeline\s*\{', script, re.IGNORECASE):
            self.errors.append("Declarative pipeline must start with 'pipeline {' block")
        
        if not re.search(r'\bagent\s+', script, re.IGNORECASE):
            self.errors.append("Declarative pipeline must specify an agent")
        
        if not re.search(r'\bstages\s*\{', script, re.IGNORECASE):
            self.errors.append("Declarative pipeline must have a 'stages' block")
    
    def _validate_scripted_pipeline(self, script: str) -> None:
        """Validate scripted pipeline syntax."""
        if not re.search(r'\bnode\s*[\(\{]', script, re.IGNORECASE):
            self.warnings.append("Scripted pipeline typically uses 'node' block")
    
    def _validate_common_syntax(self, script: str) -> None:
        """Validate common pipeline syntax issues."""
        open_braces = script.count('{')
        close_braces = script.count('}')
        if open_braces != close_braces:
            self.errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")
    
    def _extract_used_tools(self, script: str) -> None:
        """Extract tools used in the pipeline."""
        for tool in self.COMMON_TOOLS:
            if re.search(rf'\b{re.escape(tool)}\s*[\(\{{]', script, re.IGNORECASE):
                self.used_tools.add(tool)
    
    def _extract_shared_libraries(self, script: str) -> None:
        """Extract shared library functions used in the pipeline."""
        library_imports = re.findall(r'@Library\s*\(\s*[\'"]([^\'"]+)[\'"]', script, re.IGNORECASE)
        for lib in library_imports:
            self.used_shared_libraries.add(lib)
    
    def _get_validation_result(self) -> Dict[str, any]:
        """Get validation result dictionary."""
        return {
            'valid': len(self.errors) == 0,
            'errors': list(self.errors),
            'warnings': list(self.warnings),
            'used_tools': list(self.used_tools),
            'used_shared_libraries': list(self.used_shared_libraries),
            'tool_count': len(self.used_tools),
            'shared_library_count': len(self.used_shared_libraries)
        }


def detect_pipeline_type(script: str) -> str:
    """Detect pipeline type from script content."""
    if not script:
        return 'unknown'
    
    if re.search(r'^\s*pipeline\s*\{', script.strip(), re.IGNORECASE | re.MULTILINE):
        return 'declarative'
    
    if re.search(r'^\s*node\s*[\(\{]', script.strip(), re.IGNORECASE | re.MULTILINE):
        return 'scripted'
    
    return 'unknown'


def generate_pipeline_template(pipeline_type: str, job_name: str, **kwargs) -> str:
    """Generate a pipeline template."""
    if pipeline_type.lower() == 'declarative':
        return _generate_declarative_template(job_name, **kwargs)
    elif pipeline_type.lower() == 'scripted':
        return _generate_scripted_template(job_name, **kwargs)
    else:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")


def _generate_declarative_template(job_name: str, **kwargs) -> str:
    """Generate declarative pipeline template."""
    agent = kwargs.get('agent', 'any')
    stages = kwargs.get('stages', ['Build', 'Test', 'Deploy'])
    shared_libraries = kwargs.get('shared_libraries', [])
    
    template = ""
    
    if shared_libraries:
        for lib in shared_libraries:
            template += f"@Library('{lib}') _\n"
        template += "\n"
    
    template += "pipeline {\n"
    template += f"    agent {agent}\n\n"
    template += "    stages {\n"
    
    for stage in stages:
        template += f"        stage('{stage}') {{\n"
        template += "            steps {\n"
        template += f"                echo 'Executing {stage} stage for {job_name}'\n"
        template += "                // Add your build steps here\n"
        template += "            }\n"
        template += "        }\n"
    
    template += "    }\n"
    template += "}"
    
    return template


def _generate_scripted_template(job_name: str, **kwargs) -> str:
    """Generate scripted pipeline template."""
    node_label = kwargs.get('node_label', 'any')
    stages = kwargs.get('stages', ['Build', 'Test', 'Deploy'])
    shared_libraries = kwargs.get('shared_libraries', [])
    
    template = ""
    
    if shared_libraries:
        for lib in shared_libraries:
            template += f"@Library('{lib}') _\n"
        template += "\n"
    
    if node_label == 'any':
        template += "node {\n"
    else:
        template += f"node('{node_label}') {{\n"
    
    template += "    try {\n"
    
    for stage in stages:
        template += f"        stage('{stage}') {{\n"
        template += f"            echo 'Executing {stage} stage for {job_name}'\n"
        template += "            // Add your build steps here\n"
        template += "        }\n"
    
    template += "    } catch (Exception e) {\n"
    template += "        currentBuild.result = 'FAILURE'\n"
    template += "        throw e\n"
    template += "    }\n"
    template += "}"
    
    return template


def validate_shared_library_syntax(library_name: str) -> Tuple[bool, List[str]]:
    """Validate shared library name syntax."""
    errors = []
    
    if not library_name:
        errors.append("Library name cannot be empty")
        return False, errors
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', library_name):
        errors.append("Library name can only contain letters, numbers, underscores, and hyphens")
    
    if len(library_name) > 100:
        errors.append("Library name is too long (max 100 characters)")
    
    reserved_names = ['pipeline', 'node', 'stage', 'steps', 'script']
    if library_name.lower() in reserved_names:
        errors.append(f"'{library_name}' is a reserved name and cannot be used as library name")
    
    return len(errors) == 0, errors
