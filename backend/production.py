"""
MiroFish Production Entry Point
启动 Flask API 并托管 Vue 前端静态文件（用于 PyInstaller 打包的可执行文件）
"""

import os
import sys

# 添加后端目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import send_from_directory
from app import create_app
from app.config import Config


def get_bundle_dir():
    """获取打包资源目录（兼容 PyInstaller 和直接运行）"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def create_production_app():
    """创建生产环境 Flask 应用，同时托管前端静态文件"""
    app = create_app()
    bundle_dir = get_bundle_dir()

    frontend_dist = os.path.join(bundle_dir, 'frontend_dist')

    if not os.path.isdir(frontend_dist):
        print("警告: 未找到前端构建文件，仅启动 API 服务")
        return app

    # 静态资源目录 (JS/CSS/图片等)
    assets_dir = os.path.join(frontend_dist, 'assets')

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """托管前端构建的静态资源"""
        return send_from_directory(assets_dir, filename, max_age=31536000)

    # 静态文件目录 (项目 static/ 中的图片等)
    static_dir = os.path.join(bundle_dir, 'static')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """托管项目静态文件"""
        return send_from_directory(static_dir, filename)

    # SPA 前端路由 catch-all
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """
        托管前端 SPA:
        - 如果请求的文件存在，直接返回
        - 否则返回 index.html 让 Vue Router 处理
        """
        if path:
            file_path = os.path.join(frontend_dist, path)
            if os.path.isfile(file_path):
                return send_from_directory(frontend_dist, path)
        return send_from_directory(frontend_dist, 'index.html')

    return app


def main():
    """主函数"""
    # 验证配置
    errors = Config.validate()
    if errors:
        print("配置错误:")
        for err in errors:
            print(f"  - {err}")
        print("\n请确保以下环境变量已设置:")
        print("  LLM_API_KEY  - OpenAI 兼容的 API 密钥")
        print("  ZEP_API_KEY  - Zep 记忆服务 API 密钥")
        print("\n设置方法:")
        print("  Linux/macOS: export LLM_API_KEY=your-key")
        print("  Windows:     set LLM_API_KEY=your-key")
        sys.exit(1)

    app = create_production_app()

    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = Config.DEBUG

    print(f"\n{'=' * 50}")
    print(f"  MiroFish v0.1.0")
    print(f"  服务地址: http://{host}:{port}")
    print(f"{'=' * 50}\n")

    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()
