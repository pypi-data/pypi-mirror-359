"""
Enhanced CLI interface for dataset augmentation with iterative workflows.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

# Interactive CLI components
try:
    import inquirer
except ImportError:
    print("Please install inquirer: pip install inquirer")
    exit(1)

from .models import DatasetSample, GeneratedSample, CaseAbstract
from .augmentation_service import DatasetAugmentationService
from .braintrust_client import BraintrustClient


class DatasetAugmentationCLI:
    """Enhanced CLI for dataset augmentation with multiple workflows"""
    
    def __init__(self):
        self.service: Optional[DatasetAugmentationService] = None
        self.braintrust_client: Optional[BraintrustClient] = None
    
    def _setup_service(self) -> bool:
        """Initialize the service with API keys"""
        braintrust_api_key = os.getenv("BRAINTRUST_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY") 
        
        if not braintrust_api_key:
            print("❌ Error: BRAINTRUST_API_KEY environment variable is required")
            return False
        
        self.service = DatasetAugmentationService(braintrust_api_key)
        self.braintrust_client = BraintrustClient(braintrust_api_key)
        return True
    
    async def run(self):
        """Main CLI application entry point"""
        print("🧠 Dataset Augmentation CLI Tool")
        print("=" * 50)
        
        if not self._setup_service():
            return
        
        try:
            # Mode selection
            questions = [
                inquirer.List(
                    'mode',
                    message="Select operation mode",
                    choices=[
                        ('🔧 Augment Dataset (Interactive)', 'augment'),
                        ('📁 Upload JSON File', 'upload'),
                    ],
                )
            ]
            answers = inquirer.prompt(questions)
            
            if answers['mode'] == 'augment':
                await self._run_augmentation_workflow()
            elif answers['mode'] == 'upload':
                await self._run_upload_workflow()
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

    async def _run_upload_workflow(self):
        """Simple JSON file upload workflow"""
        print("\n📁 JSON File Upload Mode")
        print("=" * 30)
        
        # Get dataset ID
        dataset_id = await self._get_dataset_id()
        if not dataset_id:
            return
        
        # Get JSON file path
        questions = [
            inquirer.Text(
                'file_path',
                message="Enter path to JSON file containing samples",
                validate=lambda _, x: Path(x).exists() and Path(x).is_file()
            )
        ]
        answers = inquirer.prompt(questions)
        file_path = answers['file_path']
        
        # Load and validate JSON file
        try:
            with open(file_path, 'r') as f:
                samples_data = json.load(f)
            
            if not isinstance(samples_data, list):
                print("❌ JSON file must contain a list of samples")
                return
            
            print(f"📋 Loaded {len(samples_data)} samples from {file_path}")
            
            # Preview samples
            print("\n👀 Sample preview:")
            for i, sample in enumerate(samples_data[:3], 1):
                print(f"Sample {i}: {json.dumps(sample, indent=2)[:200]}{'...' if len(str(sample)) > 200 else ''}")
            
            if len(samples_data) > 3:
                print(f"... and {len(samples_data) - 3} more samples")
                
        except Exception as e:
            print(f"❌ Failed to load JSON file: {e}")
            return
        
        # Confirm upload
        questions = [
            inquirer.Confirm(
                'confirm_upload',
                message=f"Upload {len(samples_data)} samples to dataset {dataset_id}?",
                default=True
            )
        ]
        answers = inquirer.prompt(questions)
        
        if not answers['confirm_upload']:
            print("❌ Operation cancelled")
            return
        
        # Upload samples
        try:
            print(f"\n📤 Uploading {len(samples_data)} samples...")
            await self.braintrust_client.insert_samples_from_dict(dataset_id, samples_data)
            print("✅ Samples uploaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to upload samples: {e}")

    async def _run_augmentation_workflow(self):
        """Interactive dataset augmentation workflow"""
        print("\n🔧 Dataset Augmentation Mode")
        print("=" * 35)
        
        # Get dataset ID and samples
        dataset_id = await self._get_dataset_id()
        if not dataset_id:
            return
        
        samples = await self._fetch_samples(dataset_id)
        if not samples:
            return
        
        # Infer schema first
        print(f"\n🔍 Analyzing dataset schema...")
        try:
            schema = await self.service.infer_dataset_schema(samples)
            print("✅ Schema analysis complete")
        except Exception as e:
            print(f"❌ Failed to analyze schema: {e}")
            return
        
        # Get user guidance and generate case abstracts iteratively
        case_abstracts = await self._get_case_abstracts_iteratively(samples)
        if not case_abstracts:
            return
        
        # Generate samples for approved abstracts
        generated_samples = await self._generate_samples_with_review(
            case_abstracts, samples, schema
        )
        if not generated_samples:
            return
        
        # Final confirmation and upload
        await self._finalize_samples(dataset_id, generated_samples)

    async def _get_dataset_id(self) -> Optional[str]:
        """Get dataset ID from user with optional dataset listing"""
        print("\n📊 Dataset Selection")
        
        # Option to list datasets
        questions = [
            inquirer.Confirm(
                'list_datasets', 
                message="Would you like to see available datasets first?", 
                default=False
            )
        ]
        answers = inquirer.prompt(questions)
        
        if answers['list_datasets']:
            print("\n🔍 Fetching available datasets...")
            try:
                datasets = await self.braintrust_client.list_datasets()
                if datasets:
                    print("\n📋 Available Datasets:")
                    for i, dataset in enumerate(datasets[:10], 1):
                        print(f"  {i}. {dataset.get('name', 'Unnamed')} (ID: {dataset.get('id', 'Unknown')})")
                        if dataset.get('description'):
                            print(f"     Description: {dataset['description']}")
                else:
                    print("No datasets found.")
            except Exception as e:
                print(f"⚠️  Could not list datasets: {e}")
        
        questions = [
            inquirer.Text('dataset_id', message="Enter the dataset ID to augment")
        ]
        answers = inquirer.prompt(questions)
        dataset_id = answers['dataset_id']
        
        if not dataset_id.strip():
            print("❌ Dataset ID is required")
            return None
            
        return dataset_id.strip()

    async def _fetch_samples(self, dataset_id: str) -> Optional[List[DatasetSample]]:
        """Fetch samples from dataset"""
        questions = [
            inquirer.Text(
                'num_samples', 
                message="How many samples should I analyze? (recommended: 20-50)",
                default="30",
                validate=lambda _, x: x.isdigit() and int(x) > 0
            )
        ]
        answers = inquirer.prompt(questions)
        num_samples = int(answers['num_samples'])
        
        print(f"\n📥 Fetching {num_samples} samples from dataset...")
        try:
            samples = await self.braintrust_client.fetch_samples(dataset_id, num_samples)
            if not samples:
                print("❌ No samples found in dataset")
                return None
            print(f"✅ Successfully fetched {len(samples)} samples")
            return samples
        except Exception as e:
            print(f"❌ Failed to fetch samples: {e}")
            return None

    async def _get_case_abstracts_iteratively(self, samples: List[DatasetSample]) -> Optional[List[CaseAbstract]]:
        """Iteratively refine case abstracts based on user guidance"""
        print("\n💡 Test Case Generation")
        print("=" * 25)
        
        # Get initial user guidance
        questions = [
            inquirer.Text(
                'guidance',
                message="What kinds of test cases would you like me to generate?\n(e.g., 'edge cases for date parsing', 'error handling scenarios', 'boundary conditions')"
            )
        ]
        answers = inquirer.prompt(questions)
        user_guidance = answers['guidance']
        
        if not user_guidance.strip():
            print("❌ User guidance is required")
            return None
        
        # Iterative refinement loop
        feedback = ""
        while True:
            print(f"\n🔍 Generating case abstracts based on your guidance...")
            try:
                case_abstract_list = await self.service.generate_case_abstracts_with_guidance(
                    samples, user_guidance, feedback
                )
                print("✅ Case abstracts generated")
            except Exception as e:
                print(f"❌ Failed to generate case abstracts: {e}")
                return None
            
            # Show generated abstracts
            print(f"\n📋 Generated {len(case_abstract_list.abstracts)} case abstracts:")
            print("-" * 60)
            
            for i, abstract in enumerate(case_abstract_list.abstracts, 1):
                print(f"\n{i}. {abstract.title}")
                print(f"   Description: {abstract.description}")
                print(f"   Input: {abstract.expected_input_characteristics}")
                print(f"   Output: {abstract.expected_output_characteristics}")
            
            if case_abstract_list.generation_notes:
                print(f"\n📝 Notes: {case_abstract_list.generation_notes}")
            
            # User feedback/approval
            questions = [
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=[
                        ('✅ Approve these abstracts and generate samples', 'approve'),
                        ('📝 Provide feedback to refine the list', 'feedback'),
                        ('❌ Cancel', 'cancel'),
                    ],
                )
            ]
            answers = inquirer.prompt(questions)
            
            if answers['action'] == 'approve':
                return case_abstract_list.abstracts
            elif answers['action'] == 'feedback':
                questions = [
                    inquirer.Text(
                        'feedback',
                        message="What changes would you like? (e.g., 'add more error cases', 'focus on edge cases', 'remove abstract #3')"
                    )
                ]
                answers = inquirer.prompt(questions)
                feedback = answers['feedback']
                if not feedback.strip():
                    print("⚠️  No feedback provided, keeping current list")
                    return case_abstract_list.abstracts
                print(f"\n🔄 Incorporating feedback: {feedback}")
            else:  # cancel
                print("❌ Operation cancelled")
                return None

    async def _generate_samples_with_review(
        self, 
        case_abstracts: List[CaseAbstract], 
        reference_samples: List[DatasetSample],
        schema
    ) -> Optional[List[GeneratedSample]]:
        """Generate samples with individual review and variation options"""
        print(f"\n🏭 Generating {len(case_abstracts)} samples...")
        
        approved_samples = []
        
        for i, abstract in enumerate(case_abstracts, 1):
            print(f"\n📝 Generating sample {i}/{len(case_abstracts)}: {abstract.title}")
            
            try:
                current_sample = await self.service.generate_sample_for_case_abstract(
                    abstract, reference_samples, schema
                )
                print(f"✅ Generated sample for: {abstract.title}")
            except Exception as e:
                print(f"❌ Failed to generate sample for '{abstract.title}': {e}")
                continue
            
            # Review loop for this sample
            while True:
                print(f"\n👀 Review Sample {i}: {abstract.title}")
                print("-" * 40)
                print(f"Input: {json.dumps(current_sample.input, indent=2)}")
                print(f"Expected: {json.dumps(current_sample.expected, indent=2)}")
                print(f"Metadata: {json.dumps(current_sample.metadata, indent=2)}")
                print("-" * 40)
                
                questions = [
                    inquirer.List(
                        'action',
                        message="What would you like to do with this sample?",
                        choices=[
                            ('✅ Accept this sample', 'accept'),
                            ('🔄 Request a variation', 'variation'),
                            ('⏭️  Skip this sample', 'skip'),
                            ('📁 Export all samples to JSON and exit', 'export'),
                        ],
                    )
                ]
                answers = inquirer.prompt(questions)
                
                if answers['action'] == 'accept':
                    approved_samples.append(current_sample)
                    break
                elif answers['action'] == 'variation':
                    questions = [
                        inquirer.Text(
                            'variation_request',
                            message="What variation would you like? (e.g., 'make it more complex', 'use different data', 'add edge case')"
                        )
                    ]
                    answers = inquirer.prompt(questions)
                    variation_request = answers['variation_request']
                    
                    if not variation_request.strip():
                        print("⚠️  No variation request provided, keeping current sample")
                        continue
                    
                    print(f"🔄 Generating variation: {variation_request}")
                    try:
                        current_sample = await self.service.generate_sample_variation(
                            current_sample, abstract, variation_request, schema
                        )
                        print("✅ Variation generated")
                    except Exception as e:
                        print(f"❌ Failed to generate variation: {e}")
                        print("⚠️  Keeping original sample")
                elif answers['action'] == 'skip':
                    print(f"⏭️  Skipped sample: {abstract.title}")
                    break
                elif answers['action'] == 'export':
                    all_samples = approved_samples + [current_sample]
                    await self._export_to_json(all_samples)
                    return None
        
        return approved_samples

    async def _export_to_json(self, samples: List[GeneratedSample]):
        """Export samples to JSON file"""
        questions = [
            inquirer.Text(
                'export_path',
                message="Enter path for JSON export file",
                default="generated_samples.json"
            )
        ]
        answers = inquirer.prompt(questions)
        export_path = answers['export_path']
        
        try:
            export_data = []
            for sample in samples:
                export_data.append({
                    "input": sample.input,
                    "expected": sample.expected,
                    "metadata": sample.metadata
                })
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Exported {len(samples)} samples to {export_path}")
            print(f"💡 You can later upload this file using 'Upload JSON File' mode")
            
        except Exception as e:
            print(f"❌ Failed to export samples: {e}")

    async def _finalize_samples(self, dataset_id: str, samples: List[GeneratedSample]):
        """Final confirmation and upload of approved samples"""
        if not samples:
            print("❌ No samples to upload")
            return
        
        print(f"\n🎯 Final Review")
        print("=" * 15)
        print(f"Dataset ID: {dataset_id}")
        print(f"Samples to upload: {len(samples)}")
        
        questions = [
            inquirer.List(
                'final_action',
                message="Ready to upload samples to dataset?",
                choices=[
                    ('✅ Upload to dataset', 'upload'),
                    ('📁 Export to JSON file instead', 'export'),
                    ('❌ Cancel', 'cancel'),
                ],
            )
        ]
        answers = inquirer.prompt(questions)
        
        if answers['final_action'] == 'upload':
            try:
                print(f"\n📤 Uploading {len(samples)} samples to dataset...")
                await self.service.braintrust_client.insert_samples(dataset_id, samples)
                print("✅ Successfully uploaded samples to dataset!")
                
                print(f"\n🎉 Dataset Augmentation Complete!")
                print(f"   • Dataset ID: {dataset_id}")
                print(f"   • New samples created: {len(samples)}")
                
            except Exception as e:
                print(f"❌ Failed to upload samples: {e}")
                print("💡 You may want to export to JSON as backup")
        elif answers['final_action'] == 'export':
            await self._export_to_json(samples)
        else:
            print("❌ Operation cancelled")


async def main_async():
    """Async main entry point for CLI"""
    cli = DatasetAugmentationCLI()
    await cli.run()


def main():
    """Synchronous entry point for CLI (used by setuptools entry points)"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main() 