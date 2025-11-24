import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { Upload, X, FileVideo } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function VideoUpload({ token, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo'];
      if (!validTypes.includes(selectedFile.type)) {
        toast.error('Please select a valid video file (MP4, MPEG, MOV, AVI)');
        return;
      }
      
      // Validate file size (max 500MB)
      if (selectedFile.size > 500 * 1024 * 1024) {
        toast.error('File size must be less than 500MB');
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          toast.success('Video uploaded successfully!');
          onSuccess();
        } else {
          const error = JSON.parse(xhr.responseText);
          toast.error(error.detail || 'Upload failed');
          setUploading(false);
        }
      });

      xhr.addEventListener('error', () => {
        toast.error('Upload failed');
        setUploading(false);
      });

      xhr.open('POST', `${API}/videos/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
    } catch (error) {
      toast.error('Upload failed');
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50" data-testid="upload-modal">
      <Card className="w-full max-w-md border-0 shadow-2xl" style={{ background: 'rgba(255, 255, 255, 0.98)' }}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle style={{ color: '#0c4a6e' }}>Upload Video</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} data-testid="close-upload-modal">
            <X className="w-5 h-5" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-cyan-500"
            style={{ borderColor: file ? '#06b6d4' : '#cbd5e1' }}
            onClick={() => !uploading && fileInputRef.current?.click()}
            data-testid="file-drop-zone"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={handleFileSelect}
              disabled={uploading}
              data-testid="file-input"
            />
            
            {file ? (
              <div className="space-y-2">
                <FileVideo className="w-12 h-12 mx-auto" style={{ color: '#06b6d4' }} />
                <p className="font-medium" style={{ color: '#0c4a6e' }}>{file.name}</p>
                <p className="text-sm" style={{ color: '#64748b' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-12 h-12 mx-auto" style={{ color: '#94a3b8' }} />
                <p className="font-medium" style={{ color: '#64748b' }}>Click to select video</p>
                <p className="text-sm" style={{ color: '#94a3b8' }}>MP4, MPEG, MOV, AVI (max 500MB)</p>
              </div>
            )}
          </div>

          {uploading && (
            <div className="space-y-2">
              <Progress value={uploadProgress} className="h-2" />
              <p className="text-sm text-center" style={{ color: '#64748b' }}>
                Uploading: {uploadProgress}%
              </p>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={onClose}
              disabled={uploading}
              data-testid="cancel-upload-btn"
            >
              Cancel
            </Button>
            <Button
              className="flex-1 gap-2"
              onClick={handleUpload}
              disabled={!file || uploading}
              data-testid="submit-upload-btn"
              style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)' }}
            >
              <Upload className="w-4 h-4" />
              {uploading ? `Uploading ${uploadProgress}%` : 'Upload'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}