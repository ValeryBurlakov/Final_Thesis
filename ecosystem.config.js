module.exports = { 
  apps : [{
    name: 'my-diplom-bot-app',
    script: 'main.py',
    cron_restart: '0 * * * *', // автоматический рестарт каждый час
    interpreter: 'python3'
  }]
};
