Basic architecture of what this does:

1. Gets US economic data release times. Some US data are at formulaic schedules such as weekly Jobless claims on Thursday. For others, there is a module to query the Tradingview calendar api for upcoming events.
2. These get put into a Scheduler.
3. Finally, when the scheduled time arrives, it will make a request via api to the primary source (BLS,BEA,Fed etc)
4. Immediately sends the raw results in an email to a list of email addresses.
5. Makes a request using OpenAI's library to the ChatGPT API for commentary comparing previous to estimated to actual for the data release.
6. Sends a follow up email to the email list with the commentary.
