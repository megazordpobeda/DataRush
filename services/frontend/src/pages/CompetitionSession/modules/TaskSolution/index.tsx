import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Task, TaskType, Solution } from '@/shared/types/task';
import { useQuery } from '@tanstack/react-query';
import { getTaskSolutionHistory } from '@/shared/api/session';
import SolutionStatus from './components/SolutionStatus';
import InputSolution from './components/InputSolution';
import FileSolution from './components/FileSolution';
import CodeSolution from './components/CodeSolution';
import ActionButtons from './components/ActionButtons';
import SolutionHistorySheet from './components/SolutionHistorySheet';

interface TaskSolutionProps {
  task: Task;
  answer: string;
  setAnswer: (value: string) => void;
  selectedFile: File | null;
  setSelectedFile: (file: File | null) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
}

const TaskSolution: React.FC<TaskSolutionProps> = ({ 
  task, 
  answer,
  setAnswer,
  selectedFile,
  setSelectedFile, 
  onSubmit,
  isSubmitting = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [selectedSolutionUrl, setSelectedSolutionUrl] = useState<string | null>(null);
  const [displayedSolution, setDisplayedSolution] = useState<Solution | null>(null);
  const { id: competitionId } = useParams<{ id: string }>();
  const prevTaskIdRef = useRef<string | null>(null);

  const solutionsQuery = useQuery({
    queryKey: ['solutionHistory', competitionId, task.id],
    queryFn: () => getTaskSolutionHistory(competitionId || '', task.id),
    enabled: !!(competitionId && task.id),
  });

  const solutionHistory = [...(solutionsQuery.data || [])].sort((a, b) => {
    const dateA = new Date(a.timestamp);
    const dateB = new Date(b.timestamp);
    return dateA.getTime() - dateB.getTime();
  });
  
  let lastSolutionPoints = 0;
  if (solutionHistory.length > 0) {
    lastSolutionPoints = solutionHistory[solutionHistory.length - 1].earned_points 
  }
  const maxAttempts = task.max_attempts || -1;
  const submissionsUsed = solutionHistory.length;
  const submissionsLeft = Math.max(0, maxAttempts - submissionsUsed);
  const hasSubmissionsLeft = submissionsLeft > 0 || maxAttempts === -1;

  useEffect(() => {
    if (solutionHistory.length > 0 && !displayedSolution) {
      const latestSolution = solutionHistory[solutionHistory.length - 1];
      setDisplayedSolution(latestSolution);
    }
  }, [solutionHistory]);

  useEffect(() => {
    if (prevTaskIdRef.current !== task.id) {
      setDisplayedSolution(null);
      setSelectedSolutionUrl(null);
      
      if (solutionHistory.length > 0) {
        const latestSolution = solutionHistory[solutionHistory.length - 1];
        setDisplayedSolution(latestSolution);
      }
      
      prevTaskIdRef.current = task.id;
    }
  }, [task.id, solutionHistory]);

  useEffect(() => {
    const loadSolutionContent = async () => {
      if (!displayedSolution || !displayedSolution.content) return;
      try {
        if (task.type === TaskType.FILE) {
          setAnswer(""); 
          setSelectedFile(null);
          setSelectedSolutionUrl(displayedSolution.content);
        } 
        else {
          setSelectedFile(null); 
          setSelectedSolutionUrl(null);
          const response = await fetch(displayedSolution.content);
          if (!response.ok) {
            throw new Error(`Failed to fetch solution content: ${response.status}`);
          }
          const text = await response.text();

          setAnswer(text);
        }
      } catch (error) {
        console.error('Error loading solution content:', error);
      }
    };
  
    loadSolutionContent();
  }, [displayedSolution, setAnswer, setSelectedFile]);

  const handleOpenHistory = () => {
    setIsHistoryOpen(true);
  };

  const handleSolutionSelect = (solution: Solution) => {
    setDisplayedSolution(solution);
  };

  const handleClearExistingFile = () => {
    setSelectedSolutionUrl(null);
  };

  return (
    <div className="md:w-[500px] flex flex-col gap-4">
      {displayedSolution ? (
        <>
          <SolutionStatus key={displayedSolution.id} solution={displayedSolution} maxPoints={task.points}/>
        </>
      ) : (
        <div className="bg-gray-100 rounded-lg p-4 text-gray-600 font-hse-sans">
          Решение еще не отправлено
        </div>
      )}
      
      {task.type === TaskType.INPUT && (
        <InputSolution 
          answer={answer} 
          setAnswer={setAnswer} 
        />
      )}
      
      {task.type === TaskType.FILE && (
        <FileSolution 
          selectedFile={selectedFile} 
          setSelectedFile={setSelectedFile} 
          fileInputRef={fileInputRef}
          existingFileUrl={selectedSolutionUrl}
          onClearExistingFile={handleClearExistingFile}
        />
      )}
      
      {task.type === TaskType.CODE && (
        <CodeSolution 
          answer={answer} 
          setAnswer={setAnswer}
        />
      )}

      <div className={`rounded-lg p-3 font-hse-sans text-sm flex items-center 
        ${hasSubmissionsLeft 
          ? 'bg-blue-50 text-blue-700'
          : 'bg-red-50 text-red-700'}`}
      >
        {maxAttempts === -1 || hasSubmissionsLeft ? (
          <>
            <span className="font-medium">
              Осталось посылок: {maxAttempts === -1 ? '∞' : submissionsLeft}
            </span>
            {maxAttempts !== -1 && (
              <span className="text-blue-500 ml-1">
                (из {maxAttempts})
              </span>
            )}
          </>
        ) : (
          <span className="font-medium">
            Вы использовали все посылки
          </span>
        )}
      </div>

      <ActionButtons 
        onSubmit={onSubmit} 
        onHistoryClick={handleOpenHistory}
        isSubmitting={isSubmitting}
        hasSubmissionsLeft={hasSubmissionsLeft}
        isCleared={task.points === lastSolutionPoints}
      />
      
      <SolutionHistorySheet 
        isOpen={isHistoryOpen} 
        onOpenChange={setIsHistoryOpen} 
        solutions={solutionHistory}
        maxPoints={task.points}
        onSolutionSelect={handleSolutionSelect}
      />
    </div>
  );
};

export default TaskSolution;