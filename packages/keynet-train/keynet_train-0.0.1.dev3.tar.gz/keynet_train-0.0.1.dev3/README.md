# keynet-train

MLflow와 통합된 모델 훈련 유틸리티

## 설치

```bash
pip install keynet-train
```

## 주요 기능

### 🚀 완전 자동화된 훈련 API

- 모델에서 자동으로 스키마 추론
- PyTorch 모델을 ONNX로 자동 변환
- MLflow에 자동 로깅 및 버전 관리

### 📊 지원 프레임워크

- PyTorch (TorchScript, ONNX 변환)
- ONNX (네이티브 지원)
- 다중 입력/출력 모델 지원

### 🔧 MLflow 통합

- 실험 자동 생성 및 관리
- 모델 아티팩트 자동 저장
- 메트릭 및 파라미터 추적

## 사용 예제

### 자동화된 PyTorch 훈련

```python
from keynet_train import pytorch_trace_auto
import torch

# 단일 입력 모델
@pytorch_trace_auto("my_experiment", torch.randn(1, 3, 224, 224))
def train_simple_model():
    model = MyModel()

    # 훈련 로직
    optimizer = torch.optim.Adam(model.parameters())
    for epoch in range(10):
        # ... 훈련 코드 ...
        pass

    return model  # 모델만 반환!

# 다중 입력 모델
@pytorch_trace_auto("multi_input_exp", {
    "image": torch.randn(1, 3, 224, 224),
    "mask": torch.randn(1, 1, 224, 224)
})
def train_multi_input():
    model = MultiInputModel()
    # ... 훈련 ...
    return model
```

## 라이선스

MIT License
