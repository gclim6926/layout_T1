#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Graph Visualizer Flask Web Server
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
import socket
import subprocess
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# visualize.py 모듈 import
try:
    from visualize import LayoutVisualizer
    from visualize import LayoutVisualizer as LayoutVisualizer2D
    from add_addresses_lines import generate_data
    from add_lines_endpoint import add_endpoint_lines
    from add_stations import add_intra_bay_stations
    from generate_udp_data import generate_udp_data
    from check import check_data_integrity
    pass
except ImportError as e:
    print(f"모듈 import 오류: {e}")

def is_port_in_use(port):
    """포트가 사용 중인지 확인"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def kill_processes_on_port(port):
    """특정 포트를 사용하는 프로세스들을 강제 종료"""
    try:
        # macOS/Linux에서 포트를 사용하는 프로세스 찾기
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True, check=False)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔍 포트 {port}를 사용하는 프로세스 발견: {pids}")
            
            for pid in pids:
                if pid.strip():
                    try:
                        subprocess.run(['kill', '-9', pid.strip()], check=False)
                        print(f"✅ 프로세스 {pid} 강제 종료 완료")
                    except Exception as e:
                        print(f"⚠️ 프로세스 {pid} 종료 실패: {e}")
            
            # 프로세스 종료 후 잠시 대기
            import time
            time.sleep(1)
            
            # 포트가 해제되었는지 확인
            if not is_port_in_use(port):
                print(f"✅ 포트 {port} 해제 완료")
                return True
            else:
                print(f"❌ 포트 {port} 해제 실패")
                return False
        else:
            print(f"ℹ️ 포트 {port}를 사용하는 프로세스가 없습니다.")
            return True
            
    except Exception as e:
        print(f"❌ 포트 {port} 프로세스 종료 중 오류: {e}")
        return False

def ensure_port_available(port):
    """포트가 사용 가능하도록 보장"""
    if is_port_in_use(port):
        print(f"⚠️ 포트 {port}가 사용 중입니다. 프로세스를 강제 종료합니다...")
        if kill_processes_on_port(port):
            print(f"✅ 포트 {port} 사용 가능")
            return True
        else:
            print(f"❌ 포트 {port} 사용 불가. 다른 포트를 시도합니다...")
            # 다른 포트 시도
            for alt_port in [5002, 5003, 5004, 5005]:
                if not is_port_in_use(alt_port):
                    print(f"✅ 대체 포트 {alt_port} 사용 가능")
                    return alt_port
            print("❌ 사용 가능한 포트가 없습니다.")
            return None
    else:
        print(f"✅ 포트 {port} 사용 가능")
        return True

app = Flask(__name__)

# 정적 파일 경로 설정
app.static_folder = '.'
app.template_folder = '.'

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/2d-viewer', methods=['POST'])
def run_2d_viewer():
    """2D Viewer 실행"""
    try:
        data = request.get_json()
        layers = data.get('layers', [])
        components = data.get('components', [])

        visualization_mode = 'overlap'
        overlap_visualization = False

        selected_z_values = []
        if 'z6022' in layers:
            selected_z_values.append('z6022')
        if 'z4822' in layers:
            selected_z_values.append('z4822')
        if 'z0' in layers:
            selected_z_values.append('z0')

        overlap_checked = 'Overlap' in layers
        if overlap_checked:
            visualization_mode = 'overlap'
            overlap_visualization = True
        else:
            overlap_visualization = False
            if len(selected_z_values) == 1:
                visualization_mode = selected_z_values[0].lower()
            elif len(selected_z_values) >= 2:
                visualization_mode = 'multiple'
            else:
                visualization_mode = 'overlap'

        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                visualizer = LayoutVisualizer2D(
                    visualization_mode=visualization_mode,
                    overlap_visualization=overlap_visualization,
                    visualization_width=1920,
                    visualization_height=1080,
                    node_size=3,
                    selected_z_values=selected_z_values,
                    selected_components=components
                )
                try:
                    # OHTs 선택 시 2D 애니메이션 활성화
                    if isinstance(components, list) and ('ohts' in components or 'OHTs' in components):
                        visualizer.enable_oht_animation(True)
                except Exception:
                    pass
                result = visualizer.create_visualizations()
        except Exception as e:
            error_buffer.write(f"❌ LayoutVisualizer2D 실행 중 오류: {str(e)}\n")
            result = False

        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()

        return jsonify({
            'success': True,
            'message': '2D Viewer가 성공적으로 실행되었습니다.',
            'data': result,
            'layers': layers,
            'components': components,
            'execution_output': {
                'stdout': stdout_output,
                'stderr': stderr_output,
                'terminal_logs': stdout_output + stderr_output
            },
            'config_updated': {
                'visualization_mode': visualization_mode,
                'overlap_visualization': overlap_visualization,
                'overlap_checked': overlap_checked,
                'selected_layers': selected_z_values
            }
        })

    except Exception as e:
        print(f"2D Viewer 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'2D Viewer 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/3d-viewer', methods=['POST'])
def run_3d_viewer():
    """3D Viewer 실행"""
    try:
        # 요청 데이터에서 설정 가져오기
        data = request.get_json()
        layers = data.get('layers', [])
        components = data.get('components', [])
        # 출력 버퍼 기본값 초기화 (예외 발생 시에도 참조 가능하도록)
        stdout_output = ""
        stderr_output = ""
        
        print(f"3D Viewer 실행 - Layers: {layers}, Components: {components}")
        print(f"🔍 3D Components 상세 정보:")
        print(f"   components 타입: {type(components)}")
        print(f"   components 길이: {len(components) if components else 0}")
        print(f"   components 내용: {components}")
        print(f"   'addresses' in components: {'addresses' in components if components else False}")
        print(f"   'lines' in components: {'lines' in components if components else False}")
        print(f"   'stations' in components: {'stations' in components if components else False}")
        
        # Layer Filter 처리 (2D Viewer와 동일한 로직)
        selected_z_values = []
        if 'z6022' in layers:
            selected_z_values.append('z6022')
        if 'z4822' in layers:
            selected_z_values.append('z4822')
        if 'z0' in layers:
            selected_z_values.append('z0')
        
        # Overlap 체크박스가 체크되어 있는지 확인
        overlap_checked = 'Overlap' in layers
        
        if overlap_checked:
            # Overlap이 체크된 경우: 1개의 창으로 체크된 부분만 겹쳐서 표시
            visualization_mode = 'overlap'
            overlap_visualization = True
        else:
            # Overlap이 체크되지 않은 경우: 개별 모드로 설정
            overlap_visualization = False
            
            # 선택된 Z값이 1개인 경우
            if len(selected_z_values) == 1:
                visualization_mode = selected_z_values[0].lower()
            # 선택된 Z값이 2개 이상인 경우
            elif len(selected_z_values) >= 2:
                visualization_mode = 'multiple'
            # 아무것도 선택되지 않은 경우
            else:
                visualization_mode = 'overlap'  # 기본값
        
        print(f"🔍 3D Viewer Layer Filter 처리:")
        print(f"   selected_layers: {selected_z_values}")
        print(f"   overlap_mode: {overlap_visualization}")
        print(f"   visualization_mode: {visualization_mode}")
        
        # 3D 시각화 실행 (visualize_3D.py가 있다면)
        try:
            from visualize_3D import LayoutVisualizer3D
            print("✅ LayoutVisualizer3D 모듈 import 성공")
            
            print(f"🔍 LayoutVisualizer3D 생성 시 전달할 매개변수:")
            print(f"   selected_components: {components}")
            print(f"   selected_layers: {selected_z_values}")
            print(f"   overlap_mode: {overlap_visualization}")
            print(f"   visualization_mode: {visualization_mode}")
            
            # stdout과 stderr를 캡처하여 실행 결과 수집
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    visualizer = LayoutVisualizer3D(
                        selected_components=components,
                        selected_layers=selected_z_values,
                        overlap_mode=overlap_visualization,
                        visualization_mode=visualization_mode
                    )
                    print("✅ LayoutVisualizer3D 객체 생성 성공")
                    print(f"🔍 생성된 객체의 설정:")
                    print(f"   selected_components: {visualizer.selected_components}")
                    print(f"   selected_layers: {visualizer.selected_layers}")
                    print(f"   overlap_mode: {visualizer.overlap_mode}")
                    print(f"   visualization_mode: {visualizer.visualization_mode}")
                    
                    result = visualizer.create_3d_visualizations()
                    print(f"✅ 3D 시각화 생성 완료: {result}")
                    
            except Exception as e:
                error_buffer.write(f"❌ LayoutVisualizer3D 실행 중 오류: {str(e)}\n")
                result = False
            
            # 캡처된 출력 결과
            stdout_output = output_buffer.getvalue()
            stderr_output = error_buffer.getvalue()
            output_buffer.close()
            error_buffer.close()
            
        except ImportError as e:
            print(f"❌ LayoutVisualizer3D 모듈 import 실패: {e}")
            # 3D 시각화 모듈이 없는 경우 기본 2D 실행
            try:
                from visualize import LayoutVisualizer
                print("🔄 LayoutVisualizer로 대체 실행")
                visualizer = LayoutVisualizer()
                result = visualizer.create_visualizations()
            except ImportError as e2:
                print(f"❌ LayoutVisualizer도 import 실패: {e2}")
                result = False
        except Exception as e:
            print(f"❌ 3D 시각화 실행 중 오류: {e}")
            result = False
        
        return jsonify({
            'success': True,
            'message': '3D Viewer가 성공적으로 실행되었습니다.',
            'data': result,
            'layers': layers,
            'components': components,
            'execution_output': {
                'stdout': stdout_output,
                'stderr': stderr_output,
                'terminal_logs': stdout_output + stderr_output
            },
            'config_updated': {
                'selected_layers': selected_z_values,
                'overlap_mode': overlap_visualization,
                'visualization_mode': visualization_mode
            }
        })
        
    except Exception as e:
        print(f"3D Viewer 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'3D Viewer 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500



@app.route('/api/get-data', methods=['GET'])
def get_data():
    """현재 데이터 상태 확인"""
    try:
        data_files = {}
        
        # output.json 확인
        if os.path.exists('output.json'):
            with open('output.json', 'r', encoding='utf-8') as f:
                output_data = json.load(f)
                data_files['output.json'] = {
                    'addresses': len(output_data.get('addresses', [])),
                    'lines': len(output_data.get('lines', [])),
                    'stations': len(output_data.get('stations', []))
                }
        
        # layout.json 확인
        if os.path.exists('layout.json'):
            with open('layout.json', 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
                data_files['layout.json'] = {
                    'addresses': len(layout_data.get('addresses', [])),
                    'lines': len(layout_data.get('lines', [])),
                    'stations': len(layout_data.get('stations', []))
                }
        
        return jsonify({
            'success': True,
            'data': data_files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'데이터 확인 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/check-status', methods=['GET'])
def check_status():
    """서버 상태 확인"""
    return jsonify({
        'success': True,
        'status': 'running',
        'message': 'Layout Graph Visualizer 서버가 정상적으로 실행 중입니다.'
    })

@app.route('/api/get-input-data')
def get_input_data():
    """input.json 데이터 로드"""
    try:
        input_file = 'input.json'
        if not os.path.exists(input_file):
            return jsonify({
                'success': False,
                'message': f'{input_file} 파일을 찾을 수 없습니다.'
            })
        
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': input_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'input.json 로드 중 오류: {str(e)}'
        })

@app.route('/api/update-input-json', methods=['POST'])
def update_input_json():
    """input.json 업데이트"""
    try:
        data = request.get_json()
        input_file = 'input.json'
        
        # 백업 파일 생성
        import time
        backup_file = f'input_backup_{int(time.time())}.json'
        if os.path.exists(input_file):
            import shutil
            shutil.copy2(input_file, backup_file)
            print(f"✅ 백업 파일 생성: {backup_file}")
        
        # 새로운 데이터로 input.json 업데이트
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ input.json 업데이트 완료")
        
        return jsonify({
            'success': True,
            'message': 'input.json이 성공적으로 업데이트되었습니다.',
            'backup_file': backup_file
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'input.json 업데이트 중 오류: {str(e)}'
        })

@app.route('/api/run-generate', methods=['POST'])
def run_generate():
    """Generate.py 실행 (Addresses & Lines) - 직접 함수 호출"""
    try:
        print("🚀 Generate.py 실행 시작 (직접 함수 호출)")
        
        # stdout과 stderr를 캡처하여 실행 결과 수집
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # generate_data() 함수 직접 호출
                result = generate_data()
                
        except Exception as e:
            error_buffer.write(f"❌ Generate.py 실행 중 오류: {str(e)}\n")
            result = False
        
        # 캡처된 출력 결과
        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Generate.py가 성공적으로 실행되었습니다. (직접 함수 호출)',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                },
                'config_updated': {
                    'script': 'add_addresses_lines.py',
                    'status': 'completed',
                    'method': 'direct_function_call'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Generate.py 실행 중 오류가 발생했습니다.',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                }
            })
        
    except Exception as e:
        print(f"Generate.py 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Generate.py 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/run-add-lines', methods=['POST'])
def run_add_lines():
    """Add Lines 실행 - 직접 함수 호출"""
    try:
        print("🚀 Add Lines 실행 시작 (직접 함수 호출)")
        
        # stdout과 stderr를 캡처하여 실행 결과 수집
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # add_endpoint_lines() 함수 직접 호출
                add_endpoint_lines()
                result = True
                
        except Exception as e:
            error_buffer.write(f"❌ Add Lines 실행 중 오류: {str(e)}\n")
            result = False
        
        # 캡처된 출력 결과
        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Add Lines가 성공적으로 실행되었습니다. (직접 함수 호출)',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                },
                'config_updated': {
                    'script': 'add_lines_endpoint.py',
                    'status': 'completed',
                    'method': 'direct_function_call'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Add Lines 실행 중 오류가 발생했습니다.',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                }
            })
        
    except Exception as e:
        print(f"Add Lines 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Add Lines 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/run-check', methods=['POST'])
def run_check():
    """Check.py 실행 - 직접 함수 호출"""
    try:
        print("🚀 Check.py 실행 시작 (직접 함수 호출)")
        
        # stdout과 stderr를 캡처하여 실행 결과 수집
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # check_data_integrity() 함수 직접 호출
                check_data_integrity()
                result = True
                
        except Exception as e:
            error_buffer.write(f"❌ Check.py 실행 중 오류: {str(e)}\n")
            result = False
        
        # 캡처된 출력 결과
        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Check.py가 성공적으로 실행되었습니다. (직접 함수 호출)',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                },
                'config_updated': {
                    'script': 'check.py',
                    'status': 'completed',
                    'method': 'direct_function_call'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Check.py 실행 중 오류가 발생했습니다.',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                }
            })
        
    except Exception as e:
        print(f"Check.py 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Check.py 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/run-stations', methods=['POST'])
def run_stations():
    """Stations 실행 - add_stations.py의 주요 함수 실행"""
    try:
        print("🚀 Stations 실행 시작 (add_stations.py)")
        
        # stdout과 stderr를 캡처하여 실행 결과 수집
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # add_intra_bay_stations() 함수 직접 호출
                add_intra_bay_stations()
                result = True
                
        except Exception as e:
            error_buffer.write(f"❌ Stations 실행 중 오류: {str(e)}\n")
            result = False
        
        # 캡처된 출력 결과
        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Stations가 성공적으로 실행되었습니다. (add_stations.py)',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                },
                'config_updated': {
                    'script': 'add_stations.py',
                    'status': 'completed',
                    'method': 'direct_function_call'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Stations 실행 중 오류가 발생했습니다.',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                }
            })
        
    except Exception as e:
        print(f"Stations 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Stations 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/run-udp-generator', methods=['POST'])
def run_udp_generator():
    """UDP Generator 실행 - generate_udp_data.py의 주요 함수 실행"""
    try:
        print("🚀 UDP Generator 실행 시작 (generate_udp_data.py)")
        
        # 요청 데이터에서 시작 주소와 목적지 주소 가져오기
        data = request.get_json()
        start_address = data.get('start_address', 100050)
        destination_address = data.get('destination_address', 100100)
        
        print(f"🎯 UDP 데이터 생성: {start_address} → {destination_address}")
        
        # stdout과 stderr를 캡처하여 실행 결과 수집
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # generate_udp_data() 함수 직접 호출
                generate_udp_data(start_address, destination_address)
                result = True
                
        except Exception as e:
            error_buffer.write(f"❌ UDP Generator 실행 중 오류: {str(e)}\n")
            result = False
        
        # 캡처된 출력 결과
        stdout_output = output_buffer.getvalue()
        stderr_output = error_buffer.getvalue()
        output_buffer.close()
        error_buffer.close()
        
        if result:
            return jsonify({
                'success': True,
                'message': f'UDP Generator가 성공적으로 실행되었습니다. ({start_address} → {destination_address})',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                },
                'config_updated': {
                    'script': 'generate_udp_data.py',
                    'status': 'completed',
                    'method': 'direct_function_call',
                    'start_address': start_address,
                    'destination_address': destination_address
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'UDP Generator 실행 중 오류가 발생했습니다.',
                'execution_output': {
                    'stdout': stdout_output,
                    'stderr': stderr_output,
                    'terminal_logs': stdout_output + stderr_output
                }
            })
        
    except Exception as e:
        print(f"UDP Generator 실행 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'UDP Generator 실행 중 오류가 발생했습니다: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Layout Graph Visualizer Flask 서버 시작")
    
    # 포트 5001 사용 가능 여부 확인 및 해결
    port = 5001
    port_result = ensure_port_available(port)
    
    if port_result is True:
        # 원래 포트 사용
        final_port = port
        print(f"📱 브라우저에서 http://localhost:{final_port} 접속")
    elif port_result is not None:
        # 대체 포트 사용
        final_port = port_result
        print(f"📱 브라우저에서 http://localhost:{final_port} 접속 (포트 {port} 대신 {final_port} 사용)")
    else:
        # 포트 사용 불가
        print("❌ 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # Debug 모드를 False로 설정하여 자동 재시작 문제 해결
    # 보안을 위해 localhost(127.0.0.1)에서만 접근 가능하도록 설정
    app.run(debug=False, host='127.0.0.1', port=final_port)