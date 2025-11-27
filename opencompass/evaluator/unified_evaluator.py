"""Unified evaluator that integrates with the OpenCompass framework."""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from opencompass.runners import LocalRunner
from opencompass.tasks import OpenICLInferTask
from opencompass.models import UnifiedAPIModel
from opencompass.utils import build_dataset_from_cfg, build_model_from_cfg
from opencompass.partitioners import NaivePartitioner


class UnifiedEvaluator:
    """Unified evaluator for API-based model evaluation."""
    
    def __init__(self, 
                 work_dir: str = "./outputs",
                 max_workers: int = 4):
        """Initialize unified evaluator.
        
        Args:
            work_dir: Working directory for outputs
            max_workers: Maximum number of parallel workers
        """
        self.work_dir = work_dir
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        os.makedirs(work_dir, exist_ok=True)
        
    def evaluate(self,
                 model_configs: List[Dict],
                 dataset_configs: List[Dict],
                 eval_configs: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform evaluation on models and datasets.
        
        Args:
            model_configs: List of model configurations
            dataset_configs: List of dataset configurations
            eval_configs: Evaluation configurations
            
        Returns:
            Evaluation results
        """
        if eval_configs is None:
            eval_configs = {}
            
        # Build models
        models = []
        for config in model_configs:
            model = build_model_from_cfg(config)
            models.append(model)
            
        # Build datasets
        datasets = []
        for config in dataset_configs:
            dataset = build_dataset_from_cfg(config)
            datasets.append(dataset)
            
        # Partition inference tasks
        partitioner = NaivePartitioner()
        tasks = []
        for model in models:
            for dataset in datasets:
                infer_cfg = dataset.infer_cfg
                # Partition the task
                partitions = partitioner([dataset], [infer_cfg], [model.abbr])
                for partition in partitions:
                    task = OpenICLInferTask(partition)
                    tasks.append((model, dataset, task))
                    
        # Run inference tasks
        results = {}
        for model, dataset, task in tasks:
            model_abbr = model.abbr
            dataset_abbr = dataset.abbr
            
            if model_abbr not in results:
                results[model_abbr] = {}
                
            # Run task
            try:
                task.run(self.work_dir)
                # Collect results
                result_path = os.path.join(
                    self.work_dir, 
                    model_abbr, 
                    dataset_abbr, 
                    "preds.json"
                )
                if os.path.exists(result_path):
                    with open(result_path, 'r') as f:
                        preds = json.load(f)
                    results[model_abbr][dataset_abbr] = preds
            except Exception as e:
                print(f"Error running task for {model_abbr} on {dataset_abbr}: {e}")
                results[model_abbr][dataset_abbr] = {"error": str(e)}
                
        return results
        
    async def async_evaluate(self,
                             model_configs: List[Dict],
                             dataset_configs: List[Dict],
                             eval_configs: Optional[Dict] = None) -> Dict[str, Any]:
        """Asynchronously perform evaluation on models and datasets.
        
        Args:
            model_configs: List of model configurations
            dataset_configs: List of dataset configurations
            eval_configs: Evaluation configurations
            
        Returns:
            Evaluation results
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.evaluate,
            model_configs,
            dataset_configs,
            eval_configs
        )
        return result
        
    def compare_models(self,
                       cloud_model_config: Dict,
                       edge_model_config: Dict,
                       dataset_configs: List[Dict],
                       eval_configs: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare cloud and edge models.
        
        Args:
            cloud_model_config: Cloud model configuration
            edge_model_config: Edge model configuration
            dataset_configs: List of dataset configurations
            eval_configs: Evaluation configurations
            
        Returns:
            Comparison results
        """
        model_configs = [cloud_model_config, edge_model_config]
        results = self.evaluate(model_configs, dataset_configs, eval_configs)
        
        # Compare results
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "models": {
                "cloud": cloud_model_config["abbr"],
                "edge": edge_model_config["abbr"]
            },
            "datasets": [cfg["abbr"] for cfg in dataset_configs],
            "results": results,
            "comparison": {}
        }
        
        # Perform detailed comparison for each dataset
        for dataset_cfg in dataset_configs:
            dataset_abbr = dataset_cfg["abbr"]
            cloud_result = results.get(cloud_model_config["abbr"], {}).get(dataset_abbr, {})
            edge_result = results.get(edge_model_config["abbr"], {}).get(dataset_abbr, {})
            
            comparison["comparison"][dataset_abbr] = {
                "cloud": cloud_result,
                "edge": edge_result,
                "metrics": self._calculate_metrics(cloud_result, edge_result)
            }
            
        return comparison
        
    def _calculate_metrics(self, 
                          cloud_result: Dict, 
                          edge_result: Dict) -> Dict[str, float]:
        """Calculate comparison metrics.
        
        Args:
            cloud_result: Cloud model results
            edge_result: Edge model results
            
        Returns:
            Calculated metrics
        """
        metrics = {}
        
        # Accuracy comparison (simplified)
        if "accuracy" in cloud_result:
            metrics["accuracy"] = {
                "cloud": cloud_result["accuracy"],
                "edge": edge_result.get("accuracy", 0),
                "difference": cloud_result["accuracy"] - edge_result.get("accuracy", 0)
            }
            
        # Latency comparison (simplified)
        if "avg_latency" in cloud_result:
            metrics["latency"] = {
                "cloud": cloud_result["avg_latency"],
                "edge": edge_result.get("avg_latency", 0),
                "difference": edge_result.get("avg_latency", 0) - cloud_result["avg_latency"]
            }
            
        # Throughput comparison (simplified)
        if "throughput" in cloud_result:
            metrics["throughput"] = {
                "cloud": cloud_result["throughput"],
                "edge": edge_result.get("throughput", 0),
                "difference": edge_result.get("throughput", 0) - cloud_result["throughput"]
            }
            
        return metrics
        
    def generate_report(self, 
                       comparison_result: Dict,
                       output_path: Optional[str] = None) -> str:
        """Generate evaluation report.
        
        Args:
            comparison_result: Comparison results
            output_path: Output path for the report
            
        Returns:
            Report content
        """
        report = {
            "title": "AI Model Evaluation Report",
            "timestamp": comparison_result["timestamp"],
            "models": comparison_result["models"],
            "datasets": comparison_result["datasets"],
            "summary": {},
            "details": comparison_result["comparison"]
        }
        
        # Generate summary
        for dataset, comp in comparison_result["comparison"].items():
            report["summary"][dataset] = {}
            for metric, values in comp["metrics"].items():
                report["summary"][dataset][metric] = {
                    "cloud": values["cloud"],
                    "edge": values["edge"],
                    "difference": values["difference"]
                }
                
        # Save report
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
        return json.dumps(report, indent=2, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    # Example configuration
    evaluator = UnifiedEvaluator()
    
    # Define model configurations
    cloud_model_config = {
        "abbr": "gpt-3.5-turbo",
        "type": UnifiedAPIModel,
        "path": "gpt-3.5-turbo",
        "config": {
            "adapter_type": "openai",
            "api_key": "YOUR_OPENAI_API_KEY",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-3.5-turbo"
        },
        "meta_template": {
            "round": [
                {"role": "HUMAN", "api_role": "HUMAN"},
                {"role": "BOT", "api_role": "BOT", "generate": True}
            ]
        },
        "query_per_second": 1,
        "max_out_len": 2048,
        "max_seq_len": 4096,
        "batch_size": 8
    }
    
    edge_model_config = {
        "abbr": "edge-model",
        "type": UnifiedAPIModel,
        "path": "custom-edge-model",
        "config": {
            "adapter_type": "restful",
            "endpoint": "http://localhost:8000/api/v1/chat",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_TOKEN"
            },
            "request_mapping": {
                "prompt": "input.prompt",
                "max_tokens": "params.max_new_tokens"
            },
            "response_mapping": {
                "result": "data.result"
            }
        },
        "meta_template": {
            "round": [
                {"role": "HUMAN", "api_role": "HUMAN"},
                {"role": "BOT", "api_role": "BOT", "generate": True}
            ]
        },
        "query_per_second": 2,
        "max_out_len": 1024,
        "max_seq_len": 2048,
        "batch_size": 4
    }
    
    # Define dataset configurations (simplified)
    dataset_configs = [
        {
            "abbr": "gsm8k",
            "type": "GSM8KDataset",
            "path": "data/gsm8k",
            # Add other dataset configuration parameters
        }
    ]
    
    # Perform comparison
    # comparison_result = evaluator.compare_models(
    #     cloud_model_config,
    #     edge_model_config,
    #     dataset_configs
    # )
    
    # Generate report
    # report = evaluator.generate_report(comparison_result, "evaluation_report.json")
    # print(report)