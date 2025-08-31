const log = (...a) => (document.getElementById('log').textContent += a.join(' ') + '\n');

let ws, mediaStream, processor, audioCtx, micOn = false;

document.getElementById('connect').onclick = () => {
  const sid = document.getElementById('sid').value || 'user1';
  ws = new WebSocket(`ws://${location.host}/ws/${encodeURIComponent(sid)}`);
  ws.onopen = () => log('ws open');
  ws.onerror = (e) => log('ws error', e.message || e);
  ws.onclose = () => log('ws closed');
  ws.onmessage = (e) => log('event:', e.data.slice(0, 200));
};

document.getElementById('say').onclick = () => {
  if (!ws || ws.readyState !== 1) return;
  const text = prompt('Say:');
  if (text) ws.send(JSON.stringify({ type: 'text', text }));
};

document.getElementById('mic').onclick = async () => {
  if (!ws || ws.readyState !== 1) return;

  if (!micOn) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const source = audioCtx.createMediaStreamSource(mediaStream);
    const node = audioCtx.createScriptProcessor(4096, 1, 1);
    node.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      const buf = new ArrayBuffer(input.length * 2);
      const view = new DataView(buf);
      for (let i = 0; i < input.length; i++) {
        let s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
      const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
      ws.send(JSON.stringify({ type: 'audio', mime_type: 'audio/pcm', base64: b64 }));
    };
    source.connect(node);
    node.connect(audioCtx.destination);
    processor = node;
    micOn = true;
    log('mic on');
  } else {
    processor?.disconnect();
    mediaStream?.getTracks().forEach(t => t.stop());
    await audioCtx?.close();
    micOn = false;
    log('mic off');
  }
};
