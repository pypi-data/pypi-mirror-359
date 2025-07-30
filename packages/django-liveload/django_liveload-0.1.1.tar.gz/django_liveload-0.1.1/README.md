
# 🟢 Django LiveLoad

**Django LiveLoad** is a plug-and-play package for Django developers to show real-time progress updates on the frontend using WebSockets (powered by Django Channels and Daphne).

Ideal for long-running tasks like:
- Data scraping
- File processing
- ML predictions
- Background operations
---

## ✨ Built By

**Sanat Jha** - [https://sanatjha.me](https://sanatjha.me)

---

---
### **Demo Project:** [Live Load Django Demo on GitHub](https://github.com/Sanat-Jha/liveload-django-demo)

## 🚀 Features

- Live progress updates via WebSocket
- Support for both status message and percentage complete
- Works with Django templates or REST-based frontends
- `runlive` command auto-starts Daphne server
- Developer-friendly and production-ready

---

## 📦 Installation

### ✅ Step 1: Install the package

Install from PyPI (once published):

```bash
pip install django-liveload
```


---

## ⚙️ Django Project Setup

### ✅ Step 2: Add to `INSTALLED_APPS`

```python
# settings.py

INSTALLED_APPS = [
    ...
    'channels',
    'liveload',
]
```

---

### ✅ Step 3: Configure ASGI

In `settings.py`:

```python
ASGI_APPLICATION = 'your_project.routing.application' #Replace your_project name
```

Create `routing.py` in your project root (same level as `settings.py`):

```python
# your_project/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from liveload.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
```

---

### ✅ Step 4: Configure Channel Layer

For development (in-memory):

```python
# settings.py

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

For production, use Redis:

```bash
pip install channels_redis
```

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    }
}
```

---

## 🔧 Usage



### ✅ Step 5: Use in your Django view

```python
from liveload import ProgressTracker
import time

def long_task(request):
    tracker = ProgressTracker("mytask123")

    tracker.update(message="Starting...", percent=0)
    time.sleep(1)

    tracker.update(message="Step 1 complete", percent=30)
    time.sleep(1)

    tracker.update(percent=60)
    time.sleep(1)

    tracker.update(message="Finalizing...")
    time.sleep(1)

    tracker.update(message="✅ Done", percent=100)

    return render(request, "result.html")
```

> You can send either `message`, `percent`, or both. At least one is required.

---

### ✅ Step 6: Add frontend WebSocket code

```html
<script>
    const socket = new WebSocket(`ws://${window.location.host}/ws/progress/mytask123/`);
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        let text = '';
        if (data.percent !== undefined) text += `${data.percent}%`;
        if (data.status) text += (text ? ' - ' : '') + data.status;
        document.getElementById("progress-box").innerText = text;
    };
</script>

<div id="progress-box">Waiting...</div>
```

---

## 🧪 Running the Server

### ✅ Step 7: Use the custom `runlive` command

Instead of `python manage.py runserver`, use:

```bash
python manage.py runlive
```

This will:

* Automatically start the Daphne ASGI server
* Handle both HTTP and WebSocket traffic
* Replace `runserver` in your dev workflow

---

## 🧠 Example Project Structure

```
your_project/
├── your_project/
│   ├── settings.py
│   ├── routing.py         ← Channels setup
│   └── ...
├── app/
│   └── views.py           ← Use ProgressTracker here
├── templates/
│   └── your_template.html ← Add WebSocket frontend here
└── manage.py
```


---


## 📬 Support

For issues and feature requests, open a GitHub issue or contact [sanatjha4@gmail.com](mailto:sanat@example.com).

