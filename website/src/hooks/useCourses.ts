import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import { createCourse, deleteCourse, getCourses, updateCourse } from '../services/courses.service';

export function useCourses() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.courses });

  return {
    ...useQuery({
      queryKey: queryKeys.courses,
      queryFn: getCourses,
    }),
    createCourse: useMutation({ mutationFn: createCourse, onSuccess: invalidate }),
    updateCourse: useMutation({
      mutationFn: ({ courseId, payload }: { courseId: number; payload: Parameters<typeof updateCourse>[1] }) =>
        updateCourse(courseId, payload),
      onSuccess: invalidate,
    }),
    deleteCourse: useMutation({ mutationFn: deleteCourse, onSuccess: invalidate }),
  };
}
