module.exports = {
  apps: [
    {
      name: 'package-manager',
      script: './venv/bin/python',
      args: '-m uvicorn main:app --host 0.0.0.0 --port 5000',
      cwd: '/home/antal/package-manager',  // Change to your project path
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
