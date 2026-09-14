# การโปรเจกต์ children

ในขณะที่คุณสร้างคอมโพเนนต์ต่าง ๆ ขึ้นมา บางครั้งคุณอาจพบว่าตัวเองมีความต้องการที่จะ “ส่งต่อ” หรือ “โปรเจกต์” (project) โหนดลูก (children) ข้ามผ่านคอมโพเนนต์ที่ซ้อนกันหลายชั้น

## ปัญหา

ลองพิจารณาโค้ดตัวอย่างต่อไปนี้:

```rust
pub fn NestedShow<F, IV>(fallback: F, children: ChildrenFn) -> impl IntoView
where
    F: Fn() -> IV + Send + Sync + 'static,
    IV: IntoView + 'static,
{
    view! {
        <Show
            when=|| todo!()
            fallback=|| ()
        >
            <Show
                when=|| todo!()
                fallback=fallback
            >
                {children()}
            </Show>
        </Show>
    }
}
```

โค้ดนี้ดูตรงไปตรงมามาก: หากเงื่อนไขชั้นในเป็น `true` เราต้องการแสดง `children` หากไม่เป็นจริง เราต้องการแสดง `fallback` และหากเงื่อนไขชั้นนอกเป็น `false` เราก็เพียงเรนเดอร์ `()` ซึ่งหมายถึงไม่แสดงอะไรเลย

กล่าวอีกนัยหนึ่ง เราต้องการส่งผ่าน children ของ `<NestedShow/>` *ทะลุผ่าน* คอมโพเนนต์ `<Show/>` ชั้นนอก เพื่อให้มันกลายไปเป็น children ของ `<Show/>` ชั้นใน นี่คือความหมายของคำว่า “การโปรเจกต์” ที่เรากำลังพูดถึง

ทว่าโค้ดชุดนี้จะคอมไพล์ไม่ผ่าน:

```
error[E0525]: expected a closure that implements the `Fn` trait, but this closure only implements `FnOnce`
```

เหตุผลเพราะคอมโพเนนต์ `<Show/>` แต่ละตัวจำเป็นต้องมีความสามารถในการสร้าง `children` ของมันขึ้นมาใหม่ได้หลายครั้ง ในรอบแรกที่คุณสร้าง children ของ `<Show/>` ชั้นนอก มันจะยึดความเป็นเจ้าของ (ownership) ของ `fallback` และ `children` แล้วย้าย (move) พวกมันเข้าไปในการเรียกใช้ `<Show/>` ชั้นใน ทำให้หลังจากนั้นเป็นต้นไป ตัวแปรเหล่านั้นจึงไม่หลงเหลือให้หยิบมาใช้ในการสร้าง children ของ `<Show/>` ชั้นนอกในรอบถัด ๆ ไปอีกแล้ว

## รายละเอียด

> หากต้องการดูวิธีแก้ปัญหาเลย สามารถข้ามไปยังหัวข้อถัดไปได้ทันที

หากคุณต้องการทำความเข้าใจกับต้นตอของปัญหานี้อย่างลึกซึ้ง การดูโค้ดที่เกิดจากการขยายตัวของมาโคร `view` อาจช่วยให้เห็นภาพชัดเจนขึ้น นี่คือโค้ดเวอร์ชันที่ได้รับการจัดระเบียบให้อ่านง่าย:

```rust
Show(
    ShowProps::builder()
        .when(|| todo!())
        .fallback(|| ())
        .children({
            // children and fallback are moved into a closure here
            ::leptos::children::ToChildren::to_children(move || {
                Show(
                    ShowProps::builder()
                        .when(|| todo!())
                        // fallback is consumed here
                        .fallback(fallback)
                        .children({
                            // children is captured here
                            ::leptos::children::ToChildren::to_children(
                                move || children(),
                            )
                        })
                        .build(),
                )
            })
        })
        .build(),
)
```

คอมโพเนนต์ทุกตัวล้วนเป็นเจ้าของกรรมสิทธิ์ในพร็อพของตัวเอง; ดังนั้น `<Show/>` ในกรณีนี้จึงไม่สามารถถูกเรียกใช้ได้ เพราะมันมีเพียงการแคปเจอร์การอ้างอิง (captured references) ไปยัง `fallback` และ `children` เท่านั้น

## วิธีแก้ปัญหา

อย่างไรก็ตาม ทั้ง `<Suspense/>` และ `<Show/>` ต่างก็รับพารามิเตอร์เป็นชนิด `ChildrenFn` กล่าวคือ `children` ของพวกมันจะต้องอิมพลีเมนต์แทรต `Fn` เพื่อให้สามารถถูกเรียกซ้ำได้หลาย ๆ ครั้งด้วยเพียงการอ้างอิงแบบไม่เปลี่ยนรูป (immutable reference) เท่านั้น นั่นหมายความว่าเราไม่จำเป็นต้องถือครองกรรมสิทธิ์ความเป็นเจ้าของใน `children` หรือ `fallback` เลยแม้แต่น้อย เราเพียงแค่ต้องสามารถส่งผ่านการอ้างอิงแบบ `'static` ไปยังพวกมันได้ก็เพียงพอแล้ว

เราสามารถแก้ไขปัญหานี้ได้อย่างง่ายดาย โดยการเลือกใช้พรีมิตีฟ [`StoredValue`](https://docs.rs/leptos/latest/leptos/reactive/owner/struct.StoredValue.html) ซึ่งโดยหลักการแล้ว มันจะนำค่าไปฝากไว้ในระบบรีแอกทีฟ โดยส่งมอบกรรมสิทธิ์ความเป็นเจ้าของให้แก่ตัวเฟรมเวิร์ก เพื่อแลกกับการได้ตัวชี้อ้างอิงกลับมา ซึ่งคล้ายกับสัญญาณ (signals) ตรงที่เป็นประเภท `Copy` และมีอายุขัยเป็น `'static` ทำให้เราสามารถเข้าถึงหรือปรับแก้ค่าผ่านเมธอดเฉพาะทางต่าง ๆ ได้อย่างอิสระ

ในกรณีนี้ แนวทางแก้ปัญหาจึงเรียบง่ายมาก:

```rust
pub fn NestedShow<F, IV>(fallback: F, children: ChildrenFn) -> impl IntoView
where
    F: Fn() -> IV + Send + Sync + 'static,
    IV: IntoView + 'static,
{
    let fallback = StoredValue::new(fallback);
    let children = StoredValue::new(children);

    view! {
        <Show
            when=|| todo!()
            fallback=|| ()
        >
            <Show
                // check whether user is verified
                // by reading from the resource
                when=move || todo!()
                fallback=move || fallback.read_value()()
            >
                {children.read_value()()}
            </Show>
        </Show>
    }
}
```

ที่ระดับบนสุด เรานำทั้ง `fallback` และ `children` ไปจัดเก็บไว้ในขอบเขตการทำงานรีแอกทีฟ (reactive scope) ภายใต้การดูแลของ `NestedShow` จากนั้นเราก็สามารถส่งผ่านตัวอ้างอิงเหล่านั้นทะลุผ่านคอมโพเนนต์ชั้นอื่น ๆ ลงไปยังคอมโพเนนต์ `<Show/>` และสั่งเรียกใช้งานพวกมันที่นั่นได้อย่างราบรื่น

## บันทึกสุดท้าย

โปรดสังเกตว่าแนวทางนี้ทำงานได้สำเร็จเนื่องจาก `<Show/>` ต้องการเพียงการอ้างอิงแบบไม่เปลี่ยนรูปไปยัง children ของมันเท่านั้น (ซึ่ง `.read_value` สามารถมอบให้ได้) โดยไม่ต้องการกรรมสิทธิ์ความเป็นเจ้าของ

แต่ในบางกรณี คุณอาจจำเป็นต้องส่งต่อพร็อพที่ต้องถือครองกรรมสิทธิ์ (owned props) ทะลุผ่านฟังก์ชันที่รับ `ChildrenFn` ซึ่งต้องถูกเรียกซ้ำได้มากกว่าหนึ่งรอบ ในกรณีเช่นนี้ ตัวช่วยไวยากรณ์ `clone:` ภายในมาโคร `view` จะเข้ามามีบทบาทและมีประโยชน์อย่างยิ่ง

ลองพิจารณาตัวอย่างนี้:

```rust
#[component]
pub fn App() -> impl IntoView {
    let name = "Alice".to_string();
    view! {
        <Outer>
            <Inner>
                <Inmost name=name.clone()/>
            </Inner>
        </Outer>
    }
}

#[component]
pub fn Outer(children: ChildrenFn) -> impl IntoView {
    children()
}

#[component]
pub fn Inner(children: ChildrenFn) -> impl IntoView {
    children()
}

#[component]
pub fn Inmost(name: String) -> impl IntoView {
    view! {
        <p>{name}</p>
    }
}
```

แม้ว่าคุณจะเขียนว่า `name=name.clone()` แล้วก็ตาม โค้ดนี้ก็ยังคงแจ้งข้อผิดพลาดออกมาอยู่ดี:

```
cannot move out of `name`, a captured variable in an `Fn` closure
```

นั่นเป็นเพราะค่าตัวแปรถูกแคปเจอร์ทะลุผ่าน children หลายระดับชั้นที่จำเป็นต้องทำงานซ้ำได้หลายรอบ และไม่มีวิธีที่ตรงไปตรงมาในการโคลนค่าตัวแปรนั้น *เข้าไปใน* children ได้โดยตรง

ในสถานการณ์นี้ ไวยากรณ์ `clone:` จึงเป็นทางออกที่ลงตัวที่สุด การระบุ `clone:name` จะทำการโคลนค่าของ `name` *ก่อน* ที่จะย้ายมันเข้าไปไว้ใน children ของ `<Inner/>` ซึ่งช่วยคลี่คลายปัญหาเรื่องกรรมสิทธิ์ความเป็นเจ้าของได้อย่างสมบูรณ์แบบ:

```rust
view! {
	<Outer>
		<Inner clone:name>
			<Inmost name=name.clone()/>
		</Inner>
	</Outer>
}
```

ปัญหาในลักษณะนี้อาจทำความเข้าใจหรือดีบักได้ยากอยู่บ้าง เนื่องจากความทึบแสง (opacity) ของโค้ดที่สร้างขึ้นจากมาโคร `view` แต่โดยทั่วไปแล้ว มักจะมีแนวทางแก้ไขปัญหาที่เหมาะสมรองรับอยู่เสมอ
