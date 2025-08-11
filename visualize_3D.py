import json
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict
from config_3D import (
    LAYOUT_FILE, OUTPUT_FILE, Z_COLORS, VISUALIZATION_CONFIG, Z_VALUES,
    VISUALIZATION_WIDTH, VISUALIZATION_HEIGHT, VISUALIZATION_MODE, NODE_SIZE,
    OVERLAP_VISUALIZATION, INCLUDE_Z0
)

pio.renderers.default = "browser"

class LayoutVisualizer3D:
    def __init__(self, layout_file=OUTPUT_FILE):
        self.layout_file = layout_file
        self.addresses = []
        self.lines = []
        
    def load_layout_data(self):
        """layout.json 파일을 읽어서 데이터를 로드합니다."""
        try:
            with open(self.layout_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.addresses = data.get('addresses', [])
            self.lines = data.get('lines', [])
            
            print(f"✅ {self.layout_file} 파일을 성공적으로 로드했습니다.")
            print(f"📊 Addresses: {len(self.addresses)}개, Lines: {len(self.lines)}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            return False
    
    def get_color_by_z(self, z):
        """Z값에 따른 색상 반환"""
        if z == Z_VALUES['z6022']:
            return Z_COLORS[Z_VALUES['z6022']]
        elif z == Z_VALUES['z4822']:
            return Z_COLORS[Z_VALUES['z4822']]
        elif z == Z_VALUES['z0']:
            return Z_COLORS[Z_VALUES['z0']]
        else:
            return Z_COLORS['default']
    
    def filter_data_by_z(self, z_value, include=True):
        """Z값에 따라 데이터 필터링"""
        if include:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] == z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] == z_value or l['toPos']['z'] == z_value]
        else:
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] != z_value]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] != z_value and l['toPos']['z'] != z_value]
        
        return filtered_addresses, filtered_lines
    
    def filter_data_by_z0_option(self):
        """Z=0.0 포함/제외 옵션에 따라 데이터 필터링"""
        if INCLUDE_Z0:
            # Z=0.0 포함: 모든 데이터 반환
            return self.addresses, self.lines
        else:
            # Z=0.0 제외: Z=0.0이 아닌 데이터만 반환
            filtered_addresses = [a for a in self.addresses if a['pos']['z'] != Z_VALUES['z0']]
            filtered_lines = [l for l in self.lines if l['fromPos']['z'] != Z_VALUES['z0'] and l['toPos']['z'] != Z_VALUES['z0']]
            return filtered_addresses, filtered_lines
    
    def create_3d_visualization(self, addresses, lines, title):
        """3D 시각화 생성"""
        fig = go.Figure()

        # 3D 선 그리기
        if lines:
            for line in lines:
                x_coords = [line['fromPos']['x'], line['toPos']['x']]
                y_coords = [line['fromPos']['y'], line['toPos']['y']]
                z_coords = [line['fromPos']['z'], line['toPos']['z']]

                z1, z2 = line['fromPos']['z'], line['toPos']['z']
                # 4822와 6022를 연결하는 라인은 검정색, 두께 2
                if (z1 == Z_VALUES['z4822'] and z2 == Z_VALUES['z6022']) or (z1 == Z_VALUES['z6022'] and z2 == Z_VALUES['z4822']):
                    color = '#000000'  # 검정색
                    line_width = 2
                elif z1 == Z_VALUES['z6022'] or z2 == Z_VALUES['z6022']:
                    color = Z_COLORS[Z_VALUES['z6022']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                elif z1 == Z_VALUES['z4822'] or z2 == Z_VALUES['z4822']:
                    color = Z_COLORS[Z_VALUES['z4822']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                elif z1 == Z_VALUES['z0'] or z2 == Z_VALUES['z0']:
                    color = Z_COLORS[Z_VALUES['z0']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                else:
                    color = Z_COLORS['other']
                    line_width = VISUALIZATION_CONFIG['line_width']

                fig.add_trace(go.Scatter3d(
                    x=x_coords, y=y_coords, z=z_coords,
                    mode='lines',
                    line=dict(color=color, width=line_width),
                    name=f'Line {line["id"]}',
                    showlegend=False,
                    hovertemplate=f'<b>{line["name"]}</b><br>fromAddress: {line["fromAddress"]}<br>toAddress: {line["toAddress"]}<br>fromPos: ({line["fromPos"]["x"]:.2f}, {line["fromPos"]["y"]:.2f}, {line["fromPos"]["z"]:.2f})<br>toPos: ({line["toPos"]["x"]:.2f}, {line["toPos"]["y"]:.2f}, {line["toPos"]["z"]:.2f})<extra></extra>'
                ))

        # 3D 점 그리기
        if addresses:
            x_coords = [addr['pos']['x'] for addr in addresses]
            y_coords = [addr['pos']['y'] for addr in addresses]
            z_coords = [addr['pos']['z'] for addr in addresses]
            colors = [self.get_color_by_z(addr['pos']['z']) for addr in addresses]
            ids = [addr['id'] for addr in addresses]
            names = [addr['name'] for addr in addresses]

            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='markers',
                marker=dict(
                    size=NODE_SIZE,
                    color=colors,
                    line=dict(
                        color=VISUALIZATION_CONFIG['marker_border_color'],
                        width=VISUALIZATION_CONFIG['marker_border_width']
                    ),
                    opacity=0.8
                ),
                name='Addresses',
                showlegend=True,
                hovertemplate=f'<b>{title}</b><br>ID: %{{text}}<br>Name: %{{customdata}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                text=ids,
                customdata=names
            ))

        # 3D 레이아웃 설정
        fig.update_layout(
            title=title,
            width=VISUALIZATION_WIDTH,
            height=VISUALIZATION_HEIGHT,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            scene=dict(
                xaxis=dict(
                    title='X 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Y 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                zaxis=dict(
                    title='Z 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='data'
            )
        )

        return fig
    
    def create_3d_visualization_by_layer(self, addresses, lines, title):
        """Z 레이어별로 3D 시각화 생성"""
        fig = go.Figure()

        # Z 레이어별로 데이터 분리
        z_layers = {}
        for addr in addresses:
            z = addr['pos']['z']
            if z not in z_layers:
                z_layers[z] = {'addresses': [], 'lines': []}
            z_layers[z]['addresses'].append(addr)
        
        for line in lines:
            z1, z2 = line['fromPos']['z'], line['toPos']['z']
            # Z 레이어가 다른 경우 두 레이어 모두에 추가
            for z in [z1, z2]:
                if z not in z_layers:
                    z_layers[z] = {'addresses': [], 'lines': []}
                z_layers[z]['lines'].append(line)

        # 각 Z 레이어별로 시각화
        for z, data in sorted(z_layers.items()):
            layer_addresses = data['addresses']
            layer_lines = data['lines']
            
            if layer_addresses:
                x_coords = [addr['pos']['x'] for addr in layer_addresses]
                y_coords = [addr['pos']['y'] for addr in layer_addresses]
                z_coords = [addr['pos']['z'] for addr in layer_addresses]
                colors = [self.get_color_by_z(addr['pos']['z']) for addr in layer_addresses]
                ids = [addr['id'] for addr in layer_addresses]
                names = [addr['name'] for addr in layer_addresses]

                fig.add_trace(go.Scatter3d(
                    x=x_coords,
                    y=y_coords,
                    z=z_coords,
                    mode='markers',
                    marker=dict(
                        size=NODE_SIZE,
                        color=colors,
                        line=dict(
                            color=VISUALIZATION_CONFIG['marker_border_color'],
                            width=VISUALIZATION_CONFIG['marker_border_width']
                        ),
                        opacity=0.8
                    ),
                    name=f'Addresses Z={z}',
                    showlegend=True,
                    hovertemplate=f'<b>Z={z}</b><br>ID: %{{text}}<br>Name: %{{customdata}}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>',
                    text=ids,
                    customdata=names
                ))

            # 해당 레이어의 선들 그리기
            for line in layer_lines:
                x_coords = [line['fromPos']['x'], line['toPos']['x']]
                y_coords = [line['fromPos']['y'], line['toPos']['y']]
                z_coords = [line['fromPos']['z'], line['toPos']['z']]

                z1, z2 = line['fromPos']['z'], line['toPos']['z']
                # 4822와 6022를 연결하는 라인은 검정색, 두께 2
                if (z1 == Z_VALUES['z4822'] and z2 == Z_VALUES['z6022']) or (z1 == Z_VALUES['z6022'] and z2 == Z_VALUES['z4822']):
                    color = '#000000'  # 검정색
                    line_width = 2
                elif z1 == Z_VALUES['z6022'] or z2 == Z_VALUES['z6022']:
                    color = Z_COLORS[Z_VALUES['z6022']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                elif z1 == Z_VALUES['z4822'] or z2 == Z_VALUES['z4822']:
                    color = Z_COLORS[Z_VALUES['z4822']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                elif z1 == Z_VALUES['z0'] or z2 == Z_VALUES['z0']:
                    color = Z_COLORS[Z_VALUES['z0']]
                    line_width = VISUALIZATION_CONFIG['line_width']
                else:
                    color = Z_COLORS['other']
                    line_width = VISUALIZATION_CONFIG['line_width']

                fig.add_trace(go.Scatter3d(
                    x=x_coords, y=y_coords, z=z_coords,
                    mode='lines',
                    line=dict(color=color, width=line_width),
                    name=f'Line {line["id"]}',
                    showlegend=False,
                    hovertemplate=f'<b>{line["name"]}</b><br>fromAddress: {line["fromAddress"]}<br>toAddress: {line["toAddress"]}<br>fromPos: ({line["fromPos"]["x"]:.2f}, {line["fromPos"]["y"]:.2f}, {line["fromPos"]["z"]:.2f})<br>toPos: ({line["toPos"]["x"]:.2f}, {line["toPos"]["y"]:.2f}, {line["toPos"]["z"]:.2f})<extra></extra>'
                ))

        # 3D 레이아웃 설정
        fig.update_layout(
            title=title,
            width=VISUALIZATION_WIDTH,
            height=VISUALIZATION_HEIGHT,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            scene=dict(
                xaxis=dict(
                    title='X 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Y 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                zaxis=dict(
                    title='Z 좌표',
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='data'
            )
        )

        return fig
    
    def print_statistics(self, data_list, title, data_type):
        """통계 정보 출력"""
        print(f"\n📊 {title} 통계:")
        print(f"   총 {data_type} 수: {len(data_list)}")
        
        if data_list:
            if data_type == 'addresses':
                z_counts = defaultdict(int)
                for addr in data_list:
                    z_counts[addr['pos']['z']] += 1
                print("   Z값별 분포:")
                for z, count in sorted(z_counts.items()):
                    print(f"     Z={z}: {count}개")
            else:  # lines
                z_counts = defaultdict(int)
                for line in data_list:
                    z1, z2 = line['fromPos']['z'], line['toPos']['z']
                    z_key = f"{z1}→{z2}"
                    z_counts[z_key] += 1
                print("   Z값 연결 분포:")
                for z_key, count in sorted(z_counts.items()):
                    print(f"     {z_key}: {count}개")
    
    def create_3d_visualizations(self):
        """전체 3D 시각화 생성"""
        print("🚀 3D 시각화를 시작합니다...")
        
        if not self.load_layout_data():
            return False

        # Z=0.0 포함/제외 옵션 적용
        filtered_addresses, filtered_lines = self.filter_data_by_z0_option()
        
        print(f"📊 Z=0.0 포함/제외 설정: {'포함' if INCLUDE_Z0 else '제외'}")
        self.print_statistics(filtered_addresses, "필터링된 Addresses", "addresses")
        self.print_statistics(filtered_lines, "필터링된 Lines", "lines")

        addresses_z6022, lines_z6022 = self.filter_data_by_z(Z_VALUES['z6022'], include=True)
        addresses_not_z6022, lines_not_z6022 = self.filter_data_by_z(Z_VALUES['z6022'], include=False)

        # 3D 시각화 생성 (필터링된 데이터 사용)
        if VISUALIZATION_MODE == 'z6022':
            filtered_z6022_addresses = [a for a in filtered_addresses if a['pos']['z'] == Z_VALUES['z6022']]
            filtered_z6022_lines = [l for l in filtered_lines if l['fromPos']['z'] == Z_VALUES['z6022'] or l['toPos']['z'] == Z_VALUES['z6022']]
            if filtered_z6022_addresses or filtered_z6022_lines:
                fig_z6022 = self.create_3d_visualization(filtered_z6022_addresses, filtered_z6022_lines, "3D Layout Visualization - Z6022 데이터")
                fig_z6022.show()
        
        elif VISUALIZATION_MODE == 'x6022':
            filtered_not_z6022_addresses = [a for a in filtered_addresses if a['pos']['z'] != Z_VALUES['z6022']]
            filtered_not_z6022_lines = [l for l in filtered_lines if l['fromPos']['z'] != Z_VALUES['z6022'] and l['toPos']['z'] != Z_VALUES['z6022']]
            if filtered_not_z6022_addresses or filtered_not_z6022_lines:
                fig_not_z6022 = self.create_3d_visualization(filtered_not_z6022_addresses, filtered_not_z6022_lines, "3D Layout Visualization - Non-Z6022 데이터")
                fig_not_z6022.show()
        
        elif VISUALIZATION_MODE == 'both':
            if OVERLAP_VISUALIZATION:
                # 겹쳐서 보이기: 필터링된 모든 데이터를 하나의 3D 그래프에 표시
                fig_overlap = self.create_3d_visualization_by_layer(filtered_addresses, filtered_lines, "3D Layout Visualization - 모든 데이터 (레이어별)")
                fig_overlap.show()
            else:
                # 분리해서 보이기: 필터링된 데이터로 분리
                filtered_z6022_addresses = [a for a in filtered_addresses if a['pos']['z'] == Z_VALUES['z6022']]
                filtered_z6022_lines = [l for l in filtered_lines if l['fromPos']['z'] == Z_VALUES['z6022'] or l['toPos']['z'] == Z_VALUES['z6022']]
                filtered_not_z6022_addresses = [a for a in filtered_addresses if a['pos']['z'] != Z_VALUES['z6022']]
                filtered_not_z6022_lines = [l for l in filtered_lines if l['fromPos']['z'] != Z_VALUES['z6022'] and l['toPos']['z'] != Z_VALUES['z6022']]
                
                if filtered_z6022_addresses or filtered_z6022_lines:
                    fig_z6022 = self.create_3d_visualization(filtered_z6022_addresses, filtered_z6022_lines, "3D Layout Visualization - Z6022 데이터")
                    fig_z6022.show()
                
                if filtered_not_z6022_addresses or filtered_not_z6022_lines:
                    fig_not_z6022 = self.create_3d_visualization(filtered_not_z6022_addresses, filtered_not_z6022_lines, "3D Layout Visualization - Non-Z6022 데이터")
                    fig_not_z6022.show()

        print("✅ 3D 시각화가 완료되었습니다!")
        return True

def main():
    """메인 실행 함수"""
    visualizer = LayoutVisualizer3D()
    visualizer.create_3d_visualizations()

if __name__ == "__main__":
    main() 