"""
后台管理 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any
from app.core.tasks import (
    background_task_manager, 
    TaskDelay,
    AsyncTaskProcessor,
    start_background_processing,
    stop_background_processing,
    pause_background_processing,
    resume_background_processing,
    get_background_processing_status
)
from app.core.llm_factory import get_llm_manager
from app.services.llm_interface import LLMProvider
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/processing/status")
async def get_processing_status():
    """获取后台处理状态"""
    try:
        status = get_background_processing_status()
        
        # 获取处理统计
        processor = AsyncTaskProcessor()
        stats = processor.get_processing_statistics()
        
        return {
            "background_task": status,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取处理状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取处理状态失败: {str(e)}")


@router.post("/processing/start")
async def start_processing():
    """启动后台处理"""
    try:
        start_background_processing()
        return {"message": "后台处理已启动", "status": "started"}
    except Exception as e:
        logger.error(f"启动后台处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动后台处理失败: {str(e)}")


@router.post("/processing/stop")
async def stop_processing():
    """停止后台处理"""
    try:
        stop_background_processing()
        return {"message": "后台处理已停止", "status": "stopped"}
    except Exception as e:
        logger.error(f"停止后台处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止后台处理失败: {str(e)}")


@router.post("/processing/pause")
async def pause_processing(
    delay_type: str = Query(..., description="延迟类型: no_delay, ten_minutes, thirty_minutes, one_hour, one_day, forever")
):
    """暂停后台处理"""
    try:
        # 映射延迟类型
        delay_mapping = {
            "no_delay": TaskDelay.NO_DELAY,
            "ten_minutes": TaskDelay.TEN_MINUTES,
            "thirty_minutes": TaskDelay.THIRTY_MINUTES,
            "one_hour": TaskDelay.ONE_HOUR,
            "one_day": TaskDelay.ONE_DAY,
            "forever": TaskDelay.FOREVER
        }
        
        if delay_type not in delay_mapping:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的延迟类型: {delay_type}. 支持的类型: {list(delay_mapping.keys())}"
            )
        
        delay = delay_mapping[delay_type]
        pause_background_processing(delay)
        
        if delay == TaskDelay.FOREVER:
            message = "后台处理已永久暂停"
        elif delay == TaskDelay.NO_DELAY:
            message = "后台处理已恢复"
        else:
            message = f"后台处理已暂停 {delay.value} 秒"
        
        return {"message": message, "delay_type": delay_type, "delay_seconds": delay.value}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"暂停后台处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"暂停后台处理失败: {str(e)}")


@router.post("/processing/resume")
async def resume_processing():
    """恢复后台处理"""
    try:
        resume_background_processing()
        return {"message": "后台处理已恢复", "status": "resumed"}
    except Exception as e:
        logger.error(f"恢复后台处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"恢复后台处理失败: {str(e)}")


@router.post("/processing/manual-run")
async def manual_run_processing(
    limit: int = Query(10, ge=1, le=100, description="处理文章数量限制")
):
    """手动执行一次处理"""
    try:
        processor = AsyncTaskProcessor()
        result = await processor.process_pending_articles(limit)
        
        return {
            "message": "手动处理完成",
            "result": result
        }
    except Exception as e:
        logger.error(f"手动处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动处理失败: {str(e)}")


@router.post("/processing/process-today")
async def process_today_articles():
    """手动处理今日文章"""
    try:
        processor = AsyncTaskProcessor()
        result = await processor.process_today_articles()
        
        return {
            "message": "今日文章处理完成",
            "result": result
        }
    except Exception as e:
        logger.error(f"处理今日文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理今日文章失败: {str(e)}")


@router.get("/processing/statistics")
async def get_processing_statistics():
    """获取处理统计信息"""
    try:
        processor = AsyncTaskProcessor()
        stats = processor.get_processing_statistics()
        
        return {
            "message": "统计信息获取成功",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/processing/delay-options")
async def get_delay_options():
    """获取可用的延迟选项"""
    return {
        "delay_options": {
            "no_delay": {"seconds": 0, "description": "立即恢复"},
            "ten_minutes": {"seconds": 600, "description": "延迟10分钟"},
            "thirty_minutes": {"seconds": 1800, "description": "延迟30分钟"},
            "one_hour": {"seconds": 3600, "description": "延迟1小时"},
            "one_day": {"seconds": 86400, "description": "延迟1天"},
            "forever": {"seconds": -1, "description": "永久暂停"}
        }
    }


# LLM 管理相关接口
@router.get("/llm/health")
async def get_llm_health():
    """获取 LLM 服务健康状态（管理后台）"""
    try:
        llm_mgr = get_llm_manager()
        health_results = await llm_mgr.health_check_all()

        return {
            "providers": health_results,
            "active_providers": [p.value for p in llm_mgr.get_active_providers()],
            "default_provider": llm_mgr.config.default_provider.value,
        }
    except Exception as e:
        logger.error(f"获取 LLM 健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取 LLM 健康状态失败: {str(e)}")


@router.post("/llm/switch-provider")
async def switch_llm_provider(provider: str = Query(..., description="LLM 提供商")):
    """切换 LLM 提供商（管理后台）"""
    try:
        llm_mgr = get_llm_manager()

        # 验证提供商
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"不支持的提供商: {provider}")

        llm_mgr.switch_default_provider(provider_enum)

        return {
            "message": f"LLM 提供商已切换为: {provider}",
            "default_provider": provider,
        }
    except Exception as e:
        logger.error(f"切换 LLM 提供商失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换 LLM 提供商失败: {str(e)}")


@router.get("/llm/providers")
async def get_available_providers():
    """获取可用的 LLM 提供商列表"""
    try:
        providers = {}
        for provider in LLMProvider:
            providers[provider.value] = {
                "name": provider.value,
                "description": f"{provider.value.upper()} LLM Provider"
            }
        
        return {
            "providers": providers,
            "supported_providers": [p.value for p in LLMProvider]
        }
    except Exception as e:
        logger.error(f"获取提供商列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取提供商列表失败: {str(e)}")


@router.get("/articles/processing-status")
async def get_articles_processing_status(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str = Query(None, description="筛选状态: pending, processing, completed, failed")
):
    """获取文章处理状态列表（管理后台）"""
    try:
        processor = AsyncTaskProcessor()
        result = processor.get_articles_by_status(
            status=status,
            page=page,
            size=size
        )
        
        return {
            "message": "获取文章处理状态成功",
            "result": result
        }
    except Exception as e:
        logger.error(f"获取文章处理状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章处理状态失败: {str(e)}")


@router.get("/articles/processing-progress")
async def get_processing_progress():
    """获取处理进度（管理后台）"""
    try:
        processor = AsyncTaskProcessor()
        progress = processor.get_processing_progress()
        
        return {
            "message": "获取处理进度成功",
            "progress": progress
        }
    except Exception as e:
        logger.error(f"获取处理进度失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取处理进度失败: {str(e)}")
