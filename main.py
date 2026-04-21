"""
FlyVedioAssignmentAway 入口脚本
保持向后兼容，直接调用主包
"""

from fly_video_assignment_away.__main__ import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已由用户中断，再见！")
