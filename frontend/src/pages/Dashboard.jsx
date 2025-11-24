import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Upload, Video, LogOut, Play, Trash2,
  AlertTriangle, CheckCircle, Clock, FileVideo,
  LayoutDashboard, Settings, Search, Bell, Menu, X, Shield
} from 'lucide-react';
import VideoUpload from '../components/VideoUpload';
import VideoPlayer from '../components/VideoPlayer';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ user, token, socket, onLogout }) {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    fetchVideos();
  }, [filterStatus]);

  useEffect(() => {
    if (socket) {
      socket.on('processing_progress', (data) => {
        setVideos(prev => prev.map(v =>
          v.id === data.video_id
            ? { ...v, processing_progress: data.progress, status: data.status }
            : v
        ));
      });

      socket.on('processing_complete', (data) => {
        setVideos(prev => prev.map(v =>
          v.id === data.video_id
            ? { ...v, status: data.status, sensitivity: data.sensitivity, processing_progress: 100 }
            : v
        ));
        toast.success('Video processing completed!');
      });

      socket.on('processing_failed', (data) => {
        setVideos(prev => prev.map(v =>
          v.id === data.video_id
            ? { ...v, status: 'failed' }
            : v
        ));
        toast.error('Video processing failed');
      });

      return () => {
        socket.off('processing_progress');
        socket.off('processing_complete');
        socket.off('processing_failed');
      };
    }
  }, [socket]);

  const fetchVideos = async () => {
    try {
      let url = `${API}/videos`;
      const params = new URLSearchParams();
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setVideos(data);
      }
    } catch (error) {
      console.error('Failed to fetch videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = () => {
    setShowUpload(false);
    fetchVideos();
  };

  const handleDelete = async (videoId) => {
    if (!window.confirm('Are you sure you want to delete this video?')) return;

    try {
      const response = await fetch(`${API}/videos/${videoId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Video deleted successfully');
        fetchVideos();
      } else {
        toast.error('Failed to delete video');
      }
    } catch (error) {
      toast.error('Failed to delete video');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-emerald-500/10 text-emerald-600 border-emerald-200';
      case 'processing': return 'bg-blue-500/10 text-blue-600 border-blue-200';
      case 'uploading': return 'bg-amber-500/10 text-amber-600 border-amber-200';
      case 'failed': return 'bg-red-500/10 text-red-600 border-red-200';
      default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-20'
          } bg-white border-r border-slate-200 transition-all duration-300 flex flex-col fixed h-full z-20`}
      >
        <div className="p-6 flex items-center gap-3 border-b border-slate-100">
          <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-blue-500/20">
            <Video className="w-6 h-6 text-white" />
          </div>
          {sidebarOpen && (
            <span className="font-bold text-xl tracking-tight text-slate-900">
              Video<span className="text-blue-600">AI</span>
            </span>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Button variant="ghost" className="w-full justify-start gap-3 text-slate-600 hover:text-blue-600 hover:bg-blue-50">
            <LayoutDashboard className="w-5 h-5" />
            {sidebarOpen && <span>Dashboard</span>}
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-3 text-slate-600 hover:text-blue-600 hover:bg-blue-50">
            <Settings className="w-5 h-5" />
            {sidebarOpen && <span>Settings</span>}
          </Button>
        </nav>

        <div className="p-4 border-t border-slate-100">
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={onLogout}
          >
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span>Logout</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Header */}
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10 px-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Menu className="w-5 h-5 text-slate-600" />
            </Button>
            <div className="relative hidden md:block">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search videos..."
                className="pl-10 pr-4 py-2 rounded-full bg-slate-100 border-none focus:ring-2 focus:ring-blue-500/20 w-64 text-sm"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5 text-slate-600" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </Button>
            <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
              <div className="text-right hidden md:block">
                <p className="text-sm font-medium text-slate-900">{user?.username}</p>
                <p className="text-xs text-slate-500 capitalize">{user?.role}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 flex items-center justify-center text-slate-600 font-bold">
                {user?.username?.[0]?.toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-8 max-w-7xl mx-auto space-y-8">
          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: 'Total Videos', value: videos.length, color: 'text-blue-600', bg: 'bg-blue-50' },
              { label: 'Processing', value: videos.filter(v => v.status === 'processing').length, color: 'text-amber-600', bg: 'bg-amber-50' },
              { label: 'Safe Content', value: videos.filter(v => v.sensitivity === 'safe').length, color: 'text-emerald-600', bg: 'bg-emerald-50' },
              { label: 'Flagged', value: videos.filter(v => v.sensitivity === 'flagged').length, color: 'text-red-600', bg: 'bg-red-50' },
            ].map((stat, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow animate-fade-in-up" style={{ animationDelay: `${i * 100}ms` }}>
                <p className="text-sm font-medium text-slate-500 mb-2">{stat.label}</p>
                <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Action Bar */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <div className="flex gap-2">
              {['all', 'completed', 'processing'].map((status) => (
                <Button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  variant={filterStatus === status ? 'default' : 'ghost'}
                  className={`capitalize ${filterStatus === status ? 'bg-slate-900 text-white hover:bg-slate-800' : 'text-slate-600'}`}
                >
                  {status}
                </Button>
              ))}
            </div>

            {user?.role !== 'viewer' && (
              <Button
                onClick={() => setShowUpload(true)}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white shadow-lg shadow-blue-500/25"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload New Video
              </Button>
            )}
          </div>

          {/* Video Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-64 bg-slate-200 rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : videos.length === 0 ? (
            <div className="text-center py-24 bg-white rounded-3xl border border-dashed border-slate-200">
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <Video className="w-10 h-10 text-slate-300" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No videos yet</h3>
              <p className="text-slate-500 max-w-sm mx-auto mb-8">
                Upload your first video to start analyzing content with our AI engine.
              </p>
              {user?.role !== 'viewer' && (
                <Button onClick={() => setShowUpload(true)} variant="outline">
                  Upload Video
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((video, i) => (
                <div
                  key={video.id}
                  className="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden animate-fade-in-up"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  {/* Thumbnail Area */}
                  <div className="aspect-video bg-slate-100 relative overflow-hidden group-hover:ring-4 ring-blue-500/10 transition-all">
                    <div className="absolute inset-0 bg-gradient-to-tr from-slate-200 to-slate-50 flex items-center justify-center">
                      <FileVideo className="w-12 h-12 text-slate-300 group-hover:scale-110 transition-transform duration-500" />
                    </div>

                    {/* Overlay Actions */}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4 backdrop-blur-[2px]">
                      {video.status === 'completed' && (
                        <Button
                          size="icon"
                          className="rounded-full bg-white text-slate-900 hover:bg-blue-50 hover:text-blue-600 hover:scale-110 transition-all"
                          onClick={() => setSelectedVideo(video)}
                        >
                          <Play className="w-5 h-5 ml-1" />
                        </Button>
                      )}
                      {user?.role !== 'viewer' && (
                        <Button
                          size="icon"
                          variant="destructive"
                          className="rounded-full hover:scale-110 transition-all"
                          onClick={() => handleDelete(video.id)}
                        >
                          <Trash2 className="w-5 h-5" />
                        </Button>
                      )}
                    </div>

                    {/* Status Badge */}
                    <div className="absolute top-3 right-3">
                      <Badge className={`${getStatusColor(video.status)} border shadow-sm`}>
                        {video.status === 'processing' && <Clock className="w-3 h-3 mr-1 animate-spin" />}
                        {video.status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
                        {video.status === 'failed' && <AlertTriangle className="w-3 h-3 mr-1" />}
                        {video.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Content Area */}
                  <div className="p-5">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-slate-900 truncate flex-1 pr-4" title={video.original_name}>
                        {video.original_name}
                      </h3>
                    </div>

                    {video.status === 'processing' && (
                      <div className="mb-4">
                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                          <span>Processing...</span>
                          <span>{video.processing_progress}%</span>
                        </div>
                        <Progress value={video.processing_progress} className="h-1.5" />
                      </div>
                    )}

                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-50">
                      <div className="text-xs text-slate-400">
                        {(video.file_size / (1024 * 1024)).toFixed(1)} MB • {new Date(video.created_at).toLocaleDateString()}
                      </div>

                      {video.sensitivity && (
                        <Badge variant="outline" className={
                          video.sensitivity === 'safe'
                            ? 'text-emerald-600 border-emerald-200 bg-emerald-50'
                            : 'text-red-600 border-red-200 bg-red-50'
                        }>
                          {video.sensitivity === 'safe' ? <Shield className="w-3 h-3 mr-1" /> : <AlertTriangle className="w-3 h-3 mr-1" />}
                          {video.sensitivity}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      {showUpload && (
        <VideoUpload
          token={token}
          onClose={() => setShowUpload(false)}
          onSuccess={handleUploadComplete}
        />
      )}

      {selectedVideo && (
        <VideoPlayer
          video={selectedVideo}
          token={token}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </div>
  );
}