"""Pipeline handler for Jenkins MCP Server."""

from typing import Any, Dict, List, Optional

from loguru import logger

from jenkins_mcp_server.handlers.base_handler import BaseHandler
from jenkins_mcp_server.models import PipelineDefinition, PipelineDeploymentResult
from jenkins_mcp_server.utils.validation import validate_job_name, validate_pipeline_script, validate_folder_path


class PipelineHandler(BaseHandler):
    """Handler for Jenkins pipeline operations."""
    
    async def create_pipeline(
        self,
        name: str,
        script: str,
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        shared_libraries: Optional[List[str]] = None,
        pipeline_type: Optional[str] = None,
        validate_script: bool = True,
    ) -> PipelineDeploymentResult:
        """Create a Jenkins pipeline job with enhanced validation and shared library support."""
        try:
            from jenkins_mcp_server.utils.pipeline_utils import (
                PipelineValidator, 
                detect_pipeline_type,
                validate_shared_library_syntax
            )
            from jenkins_mcp_server.utils.path_utils import (
                normalize_jenkins_path,
                validate_jenkins_path
            )
            
            # Validate inputs
            name = validate_job_name(name)
            script = validate_pipeline_script(script)
            
            if folder_path:
                folder_path = normalize_jenkins_path(folder_path)
                if not validate_jenkins_path(folder_path):
                    raise JenkinsValidationError(f"Invalid folder path: {folder_path}")
                full_name = self._normalize_job_name(name, folder_path)
            else:
                full_name = name
            
            # Validate shared libraries
            if shared_libraries:
                for lib in shared_libraries:
                    is_valid, errors = validate_shared_library_syntax(lib)
                    if not is_valid:
                        raise JenkinsValidationError(f"Invalid shared library '{lib}': {'; '.join(errors)}")
            
            # Auto-detect pipeline type if not specified
            if not pipeline_type:
                pipeline_type = detect_pipeline_type(script)
                logger.info(f"Auto-detected pipeline type: {pipeline_type}")
            
            # Validate pipeline script if requested
            validation_result = None
            if validate_script:
                validator = PipelineValidator()
                validation_result = validator.validate_pipeline_script(script, pipeline_type)
                
                if not validation_result['valid']:
                    error_msg = f"Pipeline script validation failed: {'; '.join(validation_result['errors'])}"
                    if validation_result['warnings']:
                        error_msg += f" Warnings: {'; '.join(validation_result['warnings'])}"
                    raise JenkinsValidationError(error_msg)
                
                if validation_result['warnings']:
                    logger.warning(f"Pipeline script warnings: {'; '.join(validation_result['warnings'])}")
            
            # Enhance script with shared libraries if provided
            enhanced_script = script
            if shared_libraries:
                library_imports = []
                for lib in shared_libraries:
                    library_imports.append(f"@Library('{lib}') _")
                
                # Add library imports at the beginning of the script
                if library_imports:
                    enhanced_script = '\n'.join(library_imports) + '\n\n' + script
            
            # Generate pipeline configuration with enhanced script
            config_xml = self._generate_pipeline_config(enhanced_script, description, parameters)
            
            # Create the pipeline job
            await self.execute_with_retry(
                f'create_pipeline_{name}',
                self.jenkins_client.create_job,
                full_name,
                config_xml,
            )
            
            job_url = f'{self.jenkins_url}/job/{full_name.replace("/", "/job/")}/'
            
            return PipelineDeploymentResult(
                pipeline_name=name,
                created=True,
                job_url=job_url,
                config_xml=config_xml,
                message=f'Successfully created {pipeline_type} pipeline: {name}',
                validation_result=validation_result,
                shared_libraries=shared_libraries or [],
                pipeline_type=pipeline_type
            )
            
        except Exception as e:
            logger.error(f'Failed to create pipeline: {e}')
            return PipelineDeploymentResult(
                pipeline_name=name,
                created=False,
                job_url='',
                message=f'Failed to create pipeline: {str(e)}',
                validation_result=validation_result if 'validation_result' in locals() else None,
                shared_libraries=shared_libraries or [],
                pipeline_type=pipeline_type or 'unknown'
            )
    
    async def update_pipeline(
        self,
        name: str,
        script: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        shared_libraries: Optional[List[str]] = None,
        validate_script: bool = True,
    ) -> PipelineDeploymentResult:
        """Update an existing Jenkins pipeline job."""
        try:
            from jenkins_mcp_server.utils.pipeline_utils import (
                PipelineValidator, 
                detect_pipeline_type,
                validate_shared_library_syntax
            )
            
            name = validate_job_name(name)
            
            # Check if pipeline exists
            try:
                existing_job = await self.execute_with_retry(
                    f'get_job_{name}',
                    self.jenkins_client.get_job_info,
                    name
                )
            except Exception:
                return PipelineDeploymentResult(
                    pipeline_name=name,
                    created=False,
                    job_url='',
                    message=f'Pipeline {name} does not exist. Use create_pipeline instead.',
                    pipeline_type='unknown'
                )
            
            # Get current configuration if no new script provided
            current_script = script
            if not current_script:
                try:
                    current_config = await self.execute_with_retry(
                        f'get_job_config_{name}',
                        self.jenkins_client.get_job_config,
                        name
                    )
                    current_script = self._extract_script_from_config(current_config)
                except Exception as e:
                    logger.warning(f'Could not get current script: {e}')
                    current_script = ''
            
            if current_script:
                current_script = validate_pipeline_script(current_script)
            
            # Validate shared libraries
            if shared_libraries:
                for lib in shared_libraries:
                    is_valid, errors = validate_shared_library_syntax(lib)
                    if not is_valid:
                        raise JenkinsValidationError(f"Invalid shared library '{lib}': {'; '.join(errors)}")
            
            # Auto-detect pipeline type
            pipeline_type = detect_pipeline_type(current_script) if current_script else 'unknown'
            
            # Validate pipeline script if requested and provided
            validation_result = None
            if validate_script and current_script:
                validator = PipelineValidator()
                validation_result = validator.validate_pipeline_script(current_script, pipeline_type)
                
                if not validation_result['valid']:
                    error_msg = f"Pipeline script validation failed: {'; '.join(validation_result['errors'])}"
                    raise JenkinsValidationError(error_msg)
            
            # Enhance script with shared libraries if provided
            enhanced_script = current_script
            if shared_libraries and current_script:
                library_imports = [f"@Library('{lib}') _" for lib in shared_libraries]
                if library_imports:
                    enhanced_script = '\n'.join(library_imports) + '\n\n' + current_script
            
            # Generate updated pipeline configuration
            config_xml = self._generate_pipeline_config(
                enhanced_script or current_script, 
                description, 
                parameters or []
            )
            
            # Update the pipeline job
            await self.execute_with_retry(
                f'update_pipeline_{name}',
                self.jenkins_client.reconfig_job,
                name,
                config_xml,
            )
            
            job_url = f'{self.jenkins_url}/job/{name.replace("/", "/job/")}/'
            
            return PipelineDeploymentResult(
                pipeline_name=name,
                created=False,
                job_url=job_url,
                config_xml=config_xml,
                message=f'Successfully updated {pipeline_type} pipeline: {name}',
                validation_result=validation_result,
                shared_libraries=shared_libraries or [],
                pipeline_type=pipeline_type
            )
            
        except Exception as e:
            logger.error(f'Failed to update pipeline: {e}')
            return PipelineDeploymentResult(
                pipeline_name=name,
                created=False,
                job_url='',
                message=f'Failed to update pipeline: {str(e)}',
                pipeline_type='unknown'
            )
    
    def _extract_script_from_config(self, config_xml: str) -> str:
        """Extract pipeline script from Jenkins XML configuration."""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(config_xml)
            script_elements = [
                root.find('.//script'),
                root.find('.//definition/script'),
            ]
            for element in script_elements:
                if element is not None and element.text:
                    return element.text.strip()
            return ''
        except Exception as e:
            logger.debug(f'Failed to extract script from config: {e}')
            return ''
    
    def _generate_pipeline_config(
        self,
        script: str,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Generate pipeline job configuration XML."""
        
        # Generate parameters section
        params_xml = ''
        if parameters:
            param_definitions = []
            for param in parameters:
                param_type = param.get('type', 'string')
                param_name = param.get('name', '')
                param_default = param.get('default', '')
                param_desc = param.get('description', '')
                
                if param_type == 'string':
                    param_definitions.append(f'''
                        <hudson.model.StringParameterDefinition>
                            <name>{param_name}</name>
                            <description>{param_desc}</description>
                            <defaultValue>{param_default}</defaultValue>
                            <trim>false</trim>
                        </hudson.model.StringParameterDefinition>''')
                elif param_type == 'boolean':
                    param_definitions.append(f'''
                        <hudson.model.BooleanParameterDefinition>
                            <name>{param_name}</name>
                            <description>{param_desc}</description>
                            <defaultValue>{str(param_default).lower()}</defaultValue>
                        </hudson.model.BooleanParameterDefinition>''')
            
            if param_definitions:
                params_xml = f'''
                <properties>
                    <hudson.model.ParametersDefinitionProperty>
                        <parameterDefinitions>
                            {''.join(param_definitions)}
                        </parameterDefinitions>
                    </hudson.model.ParametersDefinitionProperty>
                </properties>'''
        
        config = f'''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{description or ''}</description>
  <keepDependencies>false</keepDependencies>
  {params_xml}
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''
        
        return config
    async def get_pipeline_definition(self, name: str) -> PipelineDefinition:
        """Get pipeline definition.
        
        Args:
            name: Pipeline name
            
        Returns:
            PipelineDefinition with pipeline details
        """
        try:
            from jenkins_mcp_server.utils.pipeline_utils import detect_pipeline_type
            
            name = validate_job_name(name)
            
            # Get pipeline configuration
            config_xml = await self.execute_with_retry(
                f'get_job_config_{name}',
                self.jenkins_client.get_job_config,
                name
            )
            
            # Extract script and other details
            script = self._extract_script_from_config(config_xml)
            pipeline_type = detect_pipeline_type(script)
            
            # Get job info for additional details
            job_info = await self.execute_with_retry(
                f'get_job_{name}',
                self.jenkins_client.get_job_info,
                name
            )
            
            return PipelineDefinition(
                name=name,
                pipeline_type=pipeline_type,
                script=script,
                description=job_info.get('description'),
                parameters=job_info.get('property', []),
                folder_path=job_info.get('fullName', '').rsplit('/', 1)[0] if '/' in job_info.get('fullName', '') else None
            )
            
        except Exception as e:
            logger.error(f'Failed to get pipeline definition: {e}')
            raise self._handle_jenkins_exception(e, f'Get pipeline definition for {name}')
