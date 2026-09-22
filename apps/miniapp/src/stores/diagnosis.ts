import { reactive } from "vue";
import type { DiagnosisResult, DiagnosisStage, SelectedImage } from "@/types/diagnosis";

interface DiagnosisState {
  image: SelectedImage | null;
  stage: DiagnosisStage;
  message: string;
  latestResult: DiagnosisResult | null;
}

const state = reactive<DiagnosisState>({
  image: null,
  stage: "idle",
  message: "",
  latestResult: null,
});

export function useDiagnosisStore() {
  function setImage(image: SelectedImage) {
    state.image = image;
  }

  function clearImage() {
    state.image = null;
  }

  function setStage(stage: DiagnosisStage, message = "") {
    state.stage = stage;
    state.message = message;
  }

  function setResult(result: DiagnosisResult | null) {
    state.latestResult = result;
  }

  return { state, setImage, clearImage, setStage, setResult };
}
