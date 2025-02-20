'use client';

import { useState, useCallback } from 'react';
import { ResearchRequest } from '@/types/research';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Loader2 } from "lucide-react";
import { Label } from "@/components/ui/label";

interface ResearchFormProps {
  onSubmit: (data: ResearchRequest) => Promise<void>;
  loading: boolean;
}

const MAX_FOCUS_AREAS = 5;
const MAX_TOPIC_LENGTH = 200;
const MAX_FOCUS_AREA_LENGTH = 50;

export default function ResearchForm({ onSubmit, loading }: ResearchFormProps) {
  const [formData, setFormData] = useState<ResearchRequest>({
    topic: '',
    depth: 3,
    language: 'zh',
    focus_areas: [],
  });

  const [focusArea, setFocusArea] = useState('');

  const addFocusArea = useCallback(() => {
    if (
      focusArea.trim() && 
      !formData.focus_areas.includes(focusArea) &&
      formData.focus_areas.length < MAX_FOCUS_AREAS &&
      focusArea.length <= MAX_FOCUS_AREA_LENGTH
    ) {
      setFormData(prev => ({
        ...prev,
        focus_areas: [...prev.focus_areas, focusArea.trim()]
      }));
      setFocusArea('');
    }
  }, [focusArea, formData.focus_areas]);

  const removeFocusArea = useCallback((area: string) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: prev.focus_areas.filter(a => a !== area)
    }));
  }, []);

  const handleDepthChange = useCallback((value: number[]) => {
    setFormData(prev => ({
      ...prev,
      depth: value[0]
    }));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.topic.length > MAX_TOPIC_LENGTH) {
      alert('研究主题过长');
      return;
    }
    onSubmit(formData);
  };

  return (
    <Card className="w-full">
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <div className="flex gap-2">
              <Input
                placeholder="输入研究主题，例如：人工智能在医疗领域的应用..."
                className="text-lg"
                value={formData.topic}
                onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                maxLength={MAX_TOPIC_LENGTH}
                required
              />
              <Button type="submit" disabled={loading || !formData.topic}>
                {loading ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>生成中...</span>
                  </div>
                ) : (
                  <span>开始研究</span>
                )}
              </Button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="depth-slider">研究深度 (1-5): {formData.depth}</Label>
              <Slider
                id="depth-slider"
                min={1}
                max={5}
                step={1}
                value={[formData.depth]}
                onValueChange={handleDepthChange}
                className="w-full"
              />
            </div>
          </div>

          <div className="space-y-4">
            <Label>关注领域 ({formData.focus_areas.length}/{MAX_FOCUS_AREAS})</Label>
            <div className="flex gap-2">
              <Input
                placeholder="输入关注领域，按回车添加..."
                value={focusArea}
                onChange={(e) => setFocusArea(e.target.value)}
                maxLength={MAX_FOCUS_AREA_LENGTH}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addFocusArea();
                  }
                }}
                disabled={formData.focus_areas.length >= MAX_FOCUS_AREAS}
              />
              <Button 
                type="button"
                variant="outline"
                onClick={addFocusArea}
                disabled={formData.focus_areas.length >= MAX_FOCUS_AREAS}>
                添加
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.focus_areas.map((area) => (
                <Badge key={area} variant="secondary" className="pl-3 pr-2 py-2 text-sm">
                  {area}
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0 ml-1"
                    onClick={() => removeFocusArea(area)}
                  >
                    ×
                  </Button>
                </Badge>
              ))}
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}