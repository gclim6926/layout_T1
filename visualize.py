import json
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict
from config import (
    LAYOUT_FILE,OUTPUT_FILE, Z_COLORS, VISUALIZATION_CONFIG, Z_VALUES, 
    VISUALIZATION_WIDTH, VISUALIZATION_HEIGHT, VISUALIZATION_MODE, NODE_SIZE,
    OVERLAP_VISUALIZATION
)

pio.renderers.default = "browser"

class LayoutVisualizer:
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
    
    def create_visualization(self, addresses, lines, title):
        """시각화 생성"""
        fig = go.Figure()

        # 선 그리기
        if lines:
            for line in lines:
                x_coords = [line['fromPos']['x'], line['toPos']['x']]
                y_coords = [line['fromPos']['y'], line['toPos']['y']]

                z1, z2 = line['fromPos']['z'], line['toPos']['z']
                if z1 == Z_VALUES['z6022'] or z2 == Z_VALUES['z6022']:
                    color = Z_COLORS[Z_VALUES['z6022']]
                elif z1 == Z_VALUES['z4822'] or z2 == Z_VALUES['z4822']:
                    color = Z_COLORS[Z_VALUES['z4822']]
                else:
                    color = Z_COLORS['other']

                fig.add_trace(go.Scatter(
                    x=x_coords, y=y_coords,
                    mode='lines',
                    line=dict(color=color, width=VISUALIZATION_CONFIG['line_width']),
                    name=f'Line {line["id"]}',
                    showlegend=False,
                    hovertemplate=f'<b>{line["name"]}</b><br>fromAddress: {line["fromAddress"]}<br>toAddress: {line["toAddress"]}<extra></extra>'
                ))

        # 점 그리기
        if addresses:
            x_coords = [addr['pos']['x'] for addr in addresses]
            y_coords = [addr['pos']['y'] for addr in addresses]
            colors = [self.get_color_by_z(addr['pos']['z']) for addr in addresses]
            ids = [addr['id'] for addr in addresses]

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                marker=dict(
                    size=NODE_SIZE,
                    color=colors,
                    line=dict(
                        color=VISUALIZATION_CONFIG['marker_border_color'],
                        width=VISUALIZATION_CONFIG['marker_border_width']
                    )
                ),
                name='Addresses',
                showlegend=True,
                hovertemplate=f'<b>{title}</b><br>ID: %{{text}}<br>X: %{{x}}<br>Y: %{{y}}<extra></extra>',
                text=ids
            ))

        # 레이아웃 설정
        fig.update_layout(
            title=title,
            width=VISUALIZATION_WIDTH,
            height=VISUALIZATION_HEIGHT,
            showlegend=True,
            hovermode=VISUALIZATION_CONFIG['hover_mode'],
            legend=VISUALIZATION_CONFIG['legend_position'],
            plot_bgcolor='white',
            xaxis=dict(title='X 좌표', showgrid=True, gridcolor='lightgray'),
            yaxis=dict(title='Y 좌표', showgrid=True, gridcolor='lightgray')
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
    
    def create_visualizations(self):
        """전체 시각화 생성"""
        print("🚀 시각화를 시작합니다...")
        
        if not self.load_layout_data():
            return False

        self.print_statistics(self.addresses, "전체 Addresses", "addresses")
        self.print_statistics(self.lines, "전체 Lines", "lines")

        addresses_z6022, lines_z6022 = self.filter_data_by_z(Z_VALUES['z6022'], include=True)
        addresses_not_z6022, lines_not_z6022 = self.filter_data_by_z(Z_VALUES['z6022'], include=False)

        # 시각화 생성
        if VISUALIZATION_MODE == 'z6022':
            if addresses_z6022 or lines_z6022:
                fig_z6022 = self.create_visualization(addresses_z6022, lines_z6022, "Layout Visualization - Z6022 데이터")
                fig_z6022.show()
        
        elif VISUALIZATION_MODE == 'x6022':
            if addresses_not_z6022 or lines_not_z6022:
                fig_not_z6022 = self.create_visualization(addresses_not_z6022, lines_not_z6022, "Layout Visualization - Non-Z6022 데이터")
                fig_not_z6022.show()
        
        elif VISUALIZATION_MODE == 'both':
            if OVERLAP_VISUALIZATION:
                # 겹쳐서 보이기: 모든 데이터를 하나의 그래프에 표시
                all_addresses = addresses_z6022 + addresses_not_z6022
                all_lines = lines_z6022 + lines_not_z6022
                fig_overlap = self.create_visualization(all_addresses, all_lines, "Layout Visualization - 모든 데이터 (겹쳐서 표시)")
                fig_overlap.show()
            else:
                # 분리해서 보이기: 기존 방식
                if addresses_z6022 or lines_z6022:
                    fig_z6022 = self.create_visualization(addresses_z6022, lines_z6022, "Layout Visualization - Z6022 데이터")
                    fig_z6022.show()
                
                if addresses_not_z6022 or lines_not_z6022:
                    fig_not_z6022 = self.create_visualization(addresses_not_z6022, lines_not_z6022, "Layout Visualization - Non-Z6022 데이터")
                    fig_not_z6022.show()

        print("✅ 시각화가 완료되었습니다!")
        return True

def main():
    """메인 실행 함수"""
    visualizer = LayoutVisualizer()
    visualizer.create_visualizations()

if __name__ == "__main__":
    main() 