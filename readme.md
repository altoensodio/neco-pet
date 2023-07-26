# neko-arc-GPT
![example](https://user-images.githubusercontent.com/18296611/226432416-eee1fe2b-94c1-4094-a3ba-173506b5b55d.gif)

https://user-images.githubusercontent.com/18296611/226147386-fc323e9d-e67e-4631-b590-995c9a14fb4c.mp4

<br>
Neco-Arc themed desktop pet/mascot/waifu with support for ChatGPT based on https://github.com/Shirros/desktop-pet

# Usage
Ctrl-click to drag, left-click to make noises, right-click to open menu, double-click to open ChatGPT session.

You can customize her personality by editing the prompt in ```assets\neco_arc\config.json```
<br>
Her responses will be saved to ```output.txt```

She will use your default TTS voice for now. I would like to create a custom voice for her eventually.

# Setup
1. Download and unzip
2. Run main.exe

or

1. ```$ git clone https://github.com/KN1053/neco-arc-GPT.git```
2. cd to neco-arc-GPT directory
3. Install python, then install requirements: ```$ pip install -r requirements.txt```
4. You might also need to install tkinter if using linux: ```$ sudo apt-get install python3-tk```
5. ```$ python3 main.py```

# GPT setup
1. Sign up on OpenAI and get your API key
2. Make sure you have free trial credit or a payment method set up.
3. Set OPENAI_API_KEY environment variable in Windows: ```$ setx OPENAI_API_KEY "<yourkey>"```
4. If using mac or linux (add to shell config file to make it permanent): ```export OPENAI_API_KEY=<yourkey>```

If you like the idea and would like to contribute feel free to have a look at the Issues tab.
