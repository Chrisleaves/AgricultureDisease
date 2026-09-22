import { reactive } from "vue";
import type { DiagnosisResult, DiagnosisStage, SelectedImage } from "@/types/diagnosis";

interface DiagnosisState {
  images: SelectedImage[];
  currentIndex: number;
  stage: DiagnosisStage;
  message: string;
  latestResult: DiagnosisResult | null;
}

const state = reactive<DiagnosisState>({
  images: [],
  currentIndex: 0,
  stage: "idle",
  message: "",
  latestResult: null,
});

export function useDiagnosisStore() {
  function appendImages(images: SelectedImage[]) {
    state.images.push(...images);
    if (state.images.length === images.length) state.currentIndex = 0;
  }

  function removeImage(index: number) {
    if (index < 0 || index >= state.images.length) return;
    state.images.splice(index, 1);
    state.currentIndex = Math.max(0, Math.min(state.currentIndex, state.images.length - 1));
  }

  function setCurrentIndex(index: number) {
    if (state.images.length === 0) {
      state.currentIndex = 0;
      return;
    }
    state.currentIndex = Math.max(0, Math.min(index, state.images.length - 1));
  }

  function setStage(stage: DiagnosisStage, message = "") {
    state.stage = stage;
    state.message = message;
  }

  function setResult(result: DiagnosisResult | null) {
    state.latestResult = result;
  }

  return { state, appendImages, removeImage, setCurrentIndex, setStage, setResult };
}
