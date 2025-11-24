import { useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function VideoPlayer({ video, token, onClose }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
    }
  }, [video]);

  const getSensitivityColor = (sensitivity) => {
    return sensitivity === 'safe' 
      ? 'bg-green-100 text-green-700' 
      : 'bg-red-100 text-red-700';
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50" data-testid="video-player-modal">
      <Card className="w-full max-w-4xl border-0 shadow-2xl" style={{ background: 'rgba(255, 255, 255, 0.98)' }}>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex-1">
            <CardTitle className="mb-2" style={{ color: '#0c4a6e' }}>{video.original_name}</CardTitle>
            <div className="flex gap-2">
              <Badge className="bg-green-100 text-green-700">Completed</Badge>
              {video.sensitivity && (
                <Badge className={getSensitivityColor(video.sensitivity)}>
                  {video.sensitivity}
                </Badge>
              )}
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} data-testid="close-player-btn">
            <X className="w-5 h-5" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              controls
              className="w-full h-full"
              data-testid="video-element"
            >
              <source
                src={`${API}/videos/${video.id}/stream`}
                type="video/mp4"
              />
              Your browser does not support the video tag.
            </video>
          </div>
          
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm" style={{ color: '#64748b' }}>
            <div>
              <p className="font-medium mb-1" style={{ color: '#0c4a6e' }}>File Size</p>
              <p>{(video.file_size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
            <div>
              <p className="font-medium mb-1" style={{ color: '#0c4a6e' }}>Uploaded</p>
              <p>{new Date(video.created_at).toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}