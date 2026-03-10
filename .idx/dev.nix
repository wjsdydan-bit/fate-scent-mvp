{ pkgs, ... }: {
  # 1. 사용할 도구들(패키지)을 여기에 적어줘
  packages = [
    pkgs.python311
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.pandas
    pkgs.nodejs_20 # Next.js를 위해 필요해!
  ];

  # 2. 환경이 만들어질 때 자동으로 실행할 명령들
  idx = {
    extensions = [
      "ms-python.python" # 파이썬 확장 프로그램도 알아서 깔아줘!
    ];
  };
}